from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Polygon
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from activity_map.serializers import MarkerSerializer, DataTableSerializer
from activity_map.models import Marker
from activity_map.serializers import RegionStatisticSerializer
from data_tables.models import DataTable, RegionStatistic
from reports.models import Project

from .utils import (
    adjust_markers_based_on_count,
    group_markers_by_coordinates_and_activity,
)


class MarkerListAPIView(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            ne_lat = request.GET.get("maxLat")
            sw_lat = request.GET.get("minLat")
            ne_lng = request.GET.get("maxLng")
            sw_lng = request.GET.get("minLng")

            if not all([ne_lat, sw_lat, ne_lng, sw_lng]):
                # If no coordinates are provided, return all markers
                markers = Marker.objects.all().select_related("category")
                serializer = MarkerSerializer(markers, many=True)
                return Response(serializer.data)
            else:
                try:
                    ne_lat = float(ne_lat)
                    sw_lat = float(sw_lat)
                    ne_lng = float(ne_lng)
                    sw_lng = float(sw_lng)

                    # Create a polygon for the given area
                    bbox = Polygon.from_bbox((sw_lng, sw_lat, ne_lng, ne_lat))

                    # Get the markers that are inside the specified area
                    markers = Marker.objects.filter(
                        location__within=bbox
                    ).select_related("category")
                    if not request.user.is_superuser:
                        markers = markers.filter(project__donors=request.user)
                    # Grouping markers by coordinates and activity
                    grouped_markers = group_markers_by_coordinates_and_activity(markers)
                    adjusted_markers = adjust_markers_based_on_count(grouped_markers)
                    serializer = MarkerSerializer(adjusted_markers, many=True)
                    return Response(serializer.data)

                except ValueError:
                    return Response(
                        {"error": "Invalid coordinates format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        else:
            return Response({}, 401)


class GetMarkerPhotosView(APIView):
    def get(self, request, marker_id):
        marker = get_object_or_404(Marker, id=marker_id)
        data_entries = DataTable.objects.filter(
            place__settlement=marker.place.settlement, category=marker.category
        )
        data_entries = data_entries.exclude(photo__exact="").exclude(photo__isnull=True)

        # Paginate the queryset with one item per page
        paginator = Paginator(data_entries, 1)
        page = request.GET.get("page")

        # Handle special cases for page value
        if page == "0":
            page = paginator.num_pages  # Return the last page
        elif page and int(page) > paginator.num_pages:
            page = (
                "1"  # Return the first page when page is beyond the last available page
            )

        try:
            paginated_data_entries = paginator.page(page)
        except PageNotAnInteger:
            paginated_data_entries = paginator.page(1)
        except EmptyPage:
            return Response({"error": "No more photos available"}, status=404)

        # Serialize and return the photo
        serializer = DataTableSerializer(paginated_data_entries, many=True)
        response_data = {
            "data_entries": serializer.data,
            "max_page": paginator.num_pages,  # Include the maximum page count in the response
        }
        return Response(response_data)


class RegionsListAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            user_projects = Project.objects.filter(donors=user)

            # Getting names of projects the user has donated to
            project_names = user_projects.values_list("name", flat=True).distinct()

            # Aggregate benef for regions with the same name and oblast
            regions = (
                RegionStatistic.objects.filter(project__name__in=project_names)
                .values("name", "oblast")
                .annotate(total_benef=Sum("benef"))
            )

            serializer = RegionStatisticSerializer(regions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)


@login_required
def maps(request):
    return render(request, "activity_map/map.html", {})
