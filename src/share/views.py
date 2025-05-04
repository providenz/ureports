from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from share.models import ProjectSharing
from share.forms import ShareProjectByEmailForm
from reports.models import Project


@login_required
def share_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if request.user.is_superuser:
        shared_with = ProjectSharing.objects.filter(project=project)
    else:
        shared_with = ProjectSharing.objects.filter(
            project=project, shared_by=request.user
        )

    if request.method == "POST":
        form = ShareProjectByEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user_to_share_with = CustomUser.objects.get(email=email, is_active=True)
                # Check that the user is not trying to share the project with themselves
                if user_to_share_with == request.user:
                    raise ValidationError("You can't share a project with yourself.")

                # Check if the project is already shared with the specified user
                if ProjectSharing.objects.filter(
                    project=project, shared_with=user_to_share_with
                ).exists():
                    messages.error(
                        request,
                        "This project is already shared with the specified user.",
                    )
                else:
                    # Add a user to the project in donors
                    project.donors.add(user_to_share_with)
                    # Create a record in ProjectSharing
                    ProjectSharing.objects.create(
                        project=project,
                        shared_by=request.user,
                        shared_with=user_to_share_with,
                    )
                    messages.success(
                        request, "The project has been successfully shared."
                    )
            except CustomUser.DoesNotExist:
                messages.error(request, "No user with this email was found.")
            except ValidationError as e:
                messages.error(request, e.message)
            return redirect("share_project", slug=slug)
    else:
        form = ShareProjectByEmailForm()

    return render(
        request,
        "share/share_project.html",
        {
            "form": form,
            "project": project,
            "shared_with": shared_with,
        },
    )


@login_required
def revoke_share(request, slug, user_id):
    project = get_object_or_404(Project, slug=slug)
    user_to_revoke = get_object_or_404(CustomUser, id=user_id)

    # Check if the user can revoke the license for this project
    if (
        not request.user.is_superuser
        and project.sharings.filter(
            shared_with=user_to_revoke, shared_by=request.user
        ).count()
        == 0
    ):
        return HttpResponseForbidden(
            "You don't have permission to revoke this license."
        )

    if request.method == "POST":
        # Remove the user from the project donors field
        project.donors.remove(user_to_revoke)
        project.sharings.filter(shared_with=user_to_revoke).delete()

        # Add notification of successful revocation of access
        messages.success(request, "The project access has been revoked.")

        return redirect("share_project", slug=slug)

    return render(
        request,
        "share/revoke_share.html",
        {"project": project, "user_to_revoke": user_to_revoke},
    )


@login_required
def list_projects_for_sharing(request):
    projects = Project.objects.filter(donors=request.user)
    return render(
        request, "share/list_projects_for_sharing.html", {"projects": projects}
    )


@csrf_exempt
def email_search_view(request):
    email = request.POST.get("email")
    user_exists = CustomUser.objects.filter(email=email, is_active=True).exists()
    return JsonResponse({"exists": user_exists, "email": email})


@csrf_exempt
def share_with_email_view(request):
    email = request.POST.get("email")
    project_slug = request.POST.get("project_slug")
    project = get_object_or_404(Project, slug=project_slug)
    user_to_share_with = get_object_or_404(CustomUser, email=email, is_active=True)

    # Check that the user is not trying to share the project with themselves
    if user_to_share_with == request.user:
        return JsonResponse(
            {"error": "You can't share a project with yourself."}, status=400
        )

    # Check if the project has already been shared with this user
    if ProjectSharing.objects.filter(
        project=project, shared_with=user_to_share_with
    ).exists():
        return JsonResponse(
            {"error": "This project is already shared with this user."}, status=400
        )

    # Create a record in ProjectSharing with user and date information
    sharing = ProjectSharing.objects.create(
        project=project, shared_by=request.user, shared_with=user_to_share_with
    )

    # Adding a user to the project donors field
    project.donors.add(user_to_share_with)
    project.save()  # Save the changes to the project

    # Return a JSON response with information about successful addition and additional information
    response_data = {
        "shared": True,
        "user_id": user_to_share_with.id,
        "shared_date": sharing.shared_at.strftime("%H:%M %d-%m-%Y "),
        "shared_by": request.user.username,
    }
    return JsonResponse(response_data)
