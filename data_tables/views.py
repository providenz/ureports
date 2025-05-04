import os
import json
from datetime import date
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from reports.models import Project, Category
from data_tables.forms import DataTableFilterForm
from data_tables.models import DataTable, TableDownload
from data_tables.serializers import DataTableSerializer
from data_tables.file_generation.file_generator import ReportsFileGenerator
from utils.create_choices import create_table_choices as create_choices
from data_tables.data_upload.convertor import Convertor
from django.http.response import JsonResponse


def get_datatable_fields(recieved_items):
    fields = {
        "Category Name": "category_name",
        "Gender": "gender",
        "Age": "age",
        "Oblast": "oblast",
        "Rayon": "rayon",
        "Gromada": "gromada",
        "Settlement": "settlement",
        "Total Benefeciary": "benef",
        "Female 0-4": "female_0_4",
        "Female 5-17": "female_5_17",
        "Female 18-59": "female_18_59",
        "Female 60+": "female_60plus",
        "Male 0-4": "male_0_4",
        "Male 5-17": "male_5_17",
        "Male 18-59": "male_18_59",
        "Male 60+": "male_60plus",
        "Female PWD": "female_PWD",
        "Male PWD": "male_PWD",
        "Date": "date",
    }
    for i in recieved_items:
        fields[i] = i
    return fields


def get_unique_received_item_keys(queryset):
    unique_keys = set()

    for instance in queryset:
        received_items = instance.received_items

        if received_items:
            # Deserialize JSON string to a Python dictionary
            received_items_dict = json.loads(received_items)

            # Assuming "received_items" is now a dictionary
            keys = (
                received_items_dict.keys()
                if isinstance(received_items_dict, dict)
                else []
            )

            # Update the set of unique keys
            unique_keys.update(keys)

    return list(unique_keys)


def filter_data_entries(request, data_entries):
    settlement = request.query_params.get("settlement")
    oblast = request.query_params.get("oblast")
    project = request.query_params.get("projects")
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")

    if settlement:
        data_entries = data_entries.filter(place__settlement=settlement)
    if oblast:
        data_entries = data_entries.filter(place__oblast=oblast)
    if date_from:
        data_entries = data_entries.filter(date__gte=date_from)
    if date_to:
        data_entries = data_entries.filter(date__lte=date_to)
    if project:
        data_entries = data_entries.filter(project__name=project)

    return data_entries


@login_required
def tables(request):
    if request.user.is_superuser:
        data_entries = DataTable.objects.all()
    else:
        data_entries = DataTable.objects.filter(project__donors=request.user)

    settlements = set(
        data_entries.values_list("place__settlement", "place__settlement").distinct()
    )
    settlements_choices = list(settlements)
    oblasts = set(data_entries.values_list("place__oblast", "place__oblast").distinct())
    oblasts_choices = [("", "All regions")] + list(oblasts)
    projects = set(
        Project.objects.filter(donors=request.user)
        .values_list("name", "name")
        .distinct()
    )
    project_choices = [("", "All projects")] + list(projects)

    filter_form = DataTableFilterForm(
        request.GET,
        settlements=settlements_choices,
        oblasts=oblasts_choices,
        projects=project_choices,
    )
    recieved_items = get_unique_received_item_keys(data_entries)

    data_table_fields = get_datatable_fields(recieved_items)
    return render(
        request,
        "data_tables/tables_base.html",
        {
            "filter_form": filter_form,
            "fields": data_table_fields,
        },
    )


class GetData(APIView):
    def get(self, request):
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("size", 20)

        if request.user.is_superuser:
            data_entries = DataTable.objects.all()
        else:
            data_entries = DataTable.objects.filter(project__donors=request.user)

        # Apply filters
        filtered_data_entries = filter_data_entries(request, data_entries)

        # Paginate the queryset
        result_page = paginator.paginate_queryset(filtered_data_entries, request)
        serializer = DataTableSerializer(result_page, many=True)

        paginated_response = {
            "last_page": paginator.page.paginator.num_pages,  # Assuming this provides the total number of pages
            "data": serializer.data,
        }

        return Response(paginated_response)


class GetTableData(APIView):
    def get(self, request, project_id, category_id=None):
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("size", 20)
        if category_id:
            data_entries = DataTable.objects.filter(
                project_id=project_id, category_id=category_id
            ).order_by("id")
        else:
            data_entries = DataTable.objects.filter(project_id=project_id).order_by(
                "-date"
            )

        filtered_data_entries = filter_data_entries(request, data_entries)

        result_page = paginator.paginate_queryset(filtered_data_entries, request)
        serializer = DataTableSerializer(result_page, many=True)

        paginated_response = {
            "last_page": paginator.page.paginator.num_pages,  # Assuming this provides the total number of pages
            "data": serializer.data,
        }

        return Response(paginated_response)


@login_required
def project_category_tables(request, project_slug, category_slug):
    project = get_object_or_404(Project, slug=project_slug)
    category = get_object_or_404(Category, slug=category_slug)

    data_entries = DataTable.objects.filter(
        project_id=project.id, category_id=category.id, project__donors=request.user
    ).order_by("id")

    settlements_choices, oblasts_choices = create_choices(data_entries)

    filter_form = DataTableFilterForm(
        request.GET, settlements=settlements_choices, oblasts=oblasts_choices
    )
    recieved_items = get_unique_received_item_keys(data_entries)
    data_table_fields = get_datatable_fields(recieved_items)

    context = {
        "project": project,
        "category": category,
        "filter_form": filter_form,
        "fields": data_table_fields,
    }
    return render(request, "data_tables/tables_detail.html", context)


class DownloadExcelFile(APIView):
    def post(self, request, project_id=None, category_id=None):
        user = request.user
        if user.is_authenticated:
            # get choosed columns from request xhr
            choosed_columns = request.data.get("choosed_columns").split(",")

            # get needed data entries
            if category_id:
                category = Category.objects.get(id=category_id)
                project = Project.objects.get(id=project_id)
                data_entries = DataTable.objects.filter(
                    project_id=project_id, category_id=category_id
                ).order_by("id")
                name = f"{project.name}_{category.name}_{date.today()}".replace(" ", "")
            elif project_id:
                project = Project.objects.get(id=project_id)
                category = None
                data_entries = DataTable.objects.filter(project_id=project_id).order_by(
                    "-date"
                )
                name = f"{project.name}_{date.today()}".replace(" ", "")
            elif not user.is_superuser:
                project = None
                category = None
                data_entries = DataTable.objects.filter(project__donors=request.user)
                name = f"ALL_{user.username}_{date.today()}".replace(" ", "")
            else:
                project = None
                category = None
                data_entries = DataTable.objects.all()
                name = f"ALL_ADMIN_{date.today()}".replace(" ", "")

            filtered_data_entries = filter_data_entries(request, data_entries)
            data_entries = DataTableSerializer(filtered_data_entries, many=True).data

            file_format = request.query_params.get("file_format")

            file_generator = ReportsFileGenerator(
                data_entries=data_entries,
                headers=choosed_columns,
                context={
                    "name": name,
                    "project": project,
                    "category": category,
                    "date": timezone.now(),
                },
            )
            xlsx_file = file_generator.generate_excel_file()
            pdf_file = file_generator.generate_pdf_file

            # Create and save the TableDownload instance to the database
            download = TableDownload.objects.create(
                user=user,
                xlsx_file=xlsx_file,
                pdf_file=pdf_file,
                name=name,
                project=project,
                category=category,
            )

            download.save()

            download_url = (
                request.build_absolute_uri(download.pdf_file.url)
                if file_format == "pdf"
                else request.build_absolute_uri(download.xlsx_file.url)
            )
            if not request.is_secure():
                download_url = download_url.replace("http://", "https://")
            return Response({"download_url": download_url})
        else:
            return Response({"Error": "Not Authorized"}, status=401)


@login_required
def generated_files_list(request):
    if request.user.is_superuser:
        files = TableDownload.objects.all().order_by("-download_date")
    else:
        files = TableDownload.objects.filter(user_id=request.user.id).order_by(
            "-download_date"
        )
    context = {
        "files": files,
    }
    return render(request, "data_tables/generated_files.html", context)


@login_required
def delete_generated_file(request, file_id):
    file = TableDownload.objects.get(id=file_id)
    if request.user == file.user or request.user.is_superuser:
        file.delete()
    return redirect("generated_files_list")


@login_required
def upload_data_page(request):
    if request.user.is_superuser:
        return render(request, "data_tables/upload_data.html")
    else:
        return redirect("index")


def upload_chunks(request):
    if request.method == "POST":
        # get file chunks and data
        zip_file_chunk = request.FILES.get("zip_file")
        xlsx_file_chunk = request.FILES.get("xlsx_file")
        index = int(request.POST.get("index"))
        total_chunks = int(request.POST.get("total_chunks"))
        temp_dir = os.path.join(settings.BASE_DIR, "tmp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        zip_temp_file = os.path.join(temp_dir, "temp_zip_file.zip")
        xlsx_temp_file = os.path.join(temp_dir, "temp_xlsx_file.xlsx")

        if index == 0:
            if os.path.exists(zip_temp_file):
                os.remove(zip_temp_file)
            if os.path.exists(xlsx_temp_file):
                os.remove(xlsx_temp_file)
            if os.path.exists(
                os.path.join(settings.BASE_DIR, "tmp", "completed_upload_data.xlsx")
            ) and os.path.exists(
                os.path.join(settings.BASE_DIR, "tmp", "complete_upload_photos.zip")
            ):
                os.remove(
                    os.path.join(settings.BASE_DIR, "tmp", "complete_upload_photos.zip")
                )
                os.remove(
                    os.path.join(settings.BASE_DIR, "tmp", "completed_upload_data.xlsx")
                )

        # handle zip file chunks
        if zip_file_chunk:
            mode = "ab" if os.path.exists(zip_temp_file) else "wb"
            with open(zip_temp_file, mode) as f:
                f.write(zip_file_chunk.read())

            if index == total_chunks - 1:
                # when file completed save it to tmp
                final_zip_file = os.path.join(
                    settings.BASE_DIR, "tmp", "complete_upload_photos.zip"
                )
                os.rename(zip_temp_file, final_zip_file)

        # handle xlsx file chunks
        if xlsx_file_chunk:
            mode = "ab" if os.path.exists(xlsx_temp_file) else "wb"
            with open(xlsx_temp_file, mode) as f:
                f.write(xlsx_file_chunk.read())
            if index == total_chunks - 1:
                # when file completed save it to tmp
                final_xlsx_file = os.path.join(
                    settings.BASE_DIR, "tmp", "completed_upload_data.xlsx"
                )
                os.rename(xlsx_temp_file, final_xlsx_file)
        zip_uploaded = os.path.exists(
            os.path.join(temp_dir, "complete_upload_photos.zip")
        )
        xlsx_uploaded = os.path.exists(
            os.path.join(temp_dir, "completed_upload_data.xlsx")
        )
        if zip_uploaded and xlsx_uploaded:
            final_xlsx_file = os.path.join(
                settings.BASE_DIR, "tmp", "completed_upload_data.xlsx"
            )
            final_zip_file = os.path.join(
                settings.BASE_DIR, "tmp", "complete_upload_photos.zip"
            )
            convertor = Convertor(xlsx_file=final_xlsx_file, zip_file=final_zip_file)
            result = convertor.extract_data_from_excel()
            created_objects = convertor.create_instances(result["data"])
            convertor.fill_dashboard()
            errors = result["errors"]
            os.remove(final_zip_file)
            os.remove(final_xlsx_file)
            return JsonResponse({"created_objects": created_objects, "errors": errors})
        return JsonResponse({"message": "Chunk received"})
    return JsonResponse({"error": "Invalid request method"})
