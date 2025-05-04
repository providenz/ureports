from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from reports.models import Project, Category
from photos.forms import DataTablePhotoFilterForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from data_tables.models import DataTable
from activity_map.models import Place
from utils.create_choices import create_photo_choices as create_choices


# View for dynamicly getting cities


def get_all_settlements(request):
    if request.user.is_superuser:
        data_entries = DataTable.objects.all()
    elif request.user.is_authenticated:
        data_entries = DataTable.objects.filter(project__donors=request.user)
    else:
        return render(request, "403.html", status=403)

    oblast = request.GET.get("oblast")
    if not oblast:
        settlements = set(
            data_entries.values_list(
                "place__settlement", "place__settlement"
            ).distinct()
        )
        settlement_choices = list(settlements)
    else:
        settlements = set(
            data_entries.filter(place__oblast=oblast)
            .values_list("place__settlement", "place__settlement")
            .distinct()
        )
        settlement_choices = list(settlements)
    return JsonResponse({"settlements": settlement_choices})


def get_settlements(request, project_slug, category_slug=None):
    project = get_object_or_404(Project, slug=project_slug)

    if (
        not request.user.is_superuser
        and not project.donors.filter(id=request.user.id).exists()
    ):
        return render(request, "403.html", status=403)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        data_entries = DataTable.objects.filter(
            project=project, category_id=category.id
        ).order_by("-date")
    else:
        data_entries = DataTable.objects.filter(project=project).order_by("-date")

    oblast = request.GET.get("oblast")
    if not oblast:
        settlements = set(
            data_entries.values_list(
                "place__settlement", "place__settlement"
            ).distinct()
        )
        settlement_choices = list(settlements)
    else:
        settlements = set(
            data_entries.filter(place__oblast=oblast)
            .values_list("place__settlement", "place__settlement")
            .distinct()
        )
        settlement_choices = list(settlements)
    return JsonResponse({"settlements": settlement_choices})


@login_required
def project_photos(request, project_slug, category_slug=None):
    project = get_object_or_404(Project, slug=project_slug)

    if (
        not request.user.is_superuser
        and not project.donors.filter(id=request.user.id).exists()
    ):
        return render(request, "403.html", status=403)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        data_entries = DataTable.objects.filter(
            project=project, category_id=category.id
        ).order_by("-date")
    else:
        data_entries = DataTable.objects.filter(project=project).order_by("-date")
        category = None

    # Get cities for current photos, and create cities choices for filtering

    settlement_choices, oblasts_choices = create_choices(data_entries)

    # Create filter form
    filter_form = DataTablePhotoFilterForm(
        request.GET, settlements=settlement_choices, oblasts=oblasts_choices
    )

    # Handle filtering
    if filter_form.is_valid():
        settlement = filter_form.cleaned_data.get("settlement")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        oblast = filter_form.cleaned_data.get("oblast")

        if settlement:
            data_entries = data_entries.filter(place__settlement__icontains=settlement)
        elif oblast:
            data_entries = data_entries.filter(place__oblast__icontains=oblast)
        if date_from:
            data_entries = data_entries.filter(date__gte=date_from)
        if date_to:
            data_entries = data_entries.filter(date__lte=date_to)

    # Get the total number of photos for the project and category
    data_entries = data_entries.exclude(photo__exact="").exclude(photo__isnull=True)

    total_photos = data_entries.count()

    # Pagination
    paginator = Paginator(data_entries, 12)
    page = request.GET.get("page")

    try:
        data_entries = paginator.page(page)
        data_entries.adjusted_elided_pages = paginator.get_elided_page_range(page)
    except PageNotAnInteger:
        data_entries = paginator.page(1)
        data_entries.adjusted_elided_pages = paginator.get_elided_page_range(1)
    except EmptyPage:
        data_entries = paginator.page(paginator.num_pages)
        data_entries.adjusted_elided_pages = paginator.get_elided_page_range(
            paginator.num_pages
        )

    if category:
        context = {
            "project": project,
            "category": category,
            "data_entries": data_entries,
            "total_photos": total_photos,
            "filter_form": filter_form,
        }

    return render(request, "photos/project_photos.html", context)


def photos(request):
    if request.user.is_superuser:
        data_entries = DataTable.objects.all()
    elif request.user.is_authenticated:
        data_entries = DataTable.objects.filter(project__donors=request.user)
    else:
        return render(request, "403.html", status=403)
    settlement_choices, oblasts_choices = create_choices(data_entries)
    projects = set(
        Project.objects.filter(donors=request.user)
        .values_list("name", "name")
        .distinct()
    )
    project_choices = [("", "All projects")] + list(projects)
    # Create filter form
    filter_form = DataTablePhotoFilterForm(
        request.GET,
        settlements=settlement_choices,
        oblasts=oblasts_choices,
        projects=project_choices,
    )

    # Handle filtering
    if filter_form.is_valid():
        settlement = filter_form.cleaned_data.get("settlement")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        oblast = filter_form.cleaned_data.get("oblast")
        projects = filter_form.cleaned_data.get("projects")

        if settlement:
            data_entries = data_entries.filter(place__settlement__icontains=settlement)
        elif oblast:
            data_entries = data_entries.filter(place__oblast__icontains=oblast)
        if date_from:
            data_entries = data_entries.filter(date__gte=date_from)
        if date_to:
            data_entries = data_entries.filter(date__lte=date_to)
        if projects:
            data_entries = data_entries.filter(project__name=projects)
    data_entries = data_entries.exclude(photo__exact="").exclude(photo__isnull=True)

    # Get the total number of photos for the project and category
    total_photos = data_entries.count()

    # Pagination
    paginator = Paginator(data_entries, 12)
    page = request.GET.get("page")

    try:
        data_entries = paginator.page(page)
        data_entries.adjusted_elided_pages = paginator.get_elided_page_range(page)
    except PageNotAnInteger:
        data_entries = paginator.page(1)
        data_entries.adjusted_elided_pages = paginator.get_elided_page_range(1)
    except EmptyPage:
        data_entries = paginator.page(paginator.num_pages)
        data_entries.adjusted_elided_pages = paginator.get_elided_page_range(
            paginator.num_pages
        )

    context = {
        "data_entries": data_entries,
        "total_photos": total_photos,
        "filter_form": filter_form,
    }
    return render(request, "photos/photos.html", context)
