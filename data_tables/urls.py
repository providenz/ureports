from django.urls import path
from . import views

urlpatterns = [
    path("tables/", views.tables, name="tables"),
    path("api/get-data/", views.GetData.as_view(), name="get-data"),
    path(
        "api/project/<int:project_id>/tables/",
        views.GetTableData.as_view(),
        name="api_project_tables",
    ),
    path(
        "api/project/<int:project_id>/category/<int:category_id>/generate_file/",
        views.DownloadExcelFile.as_view(),
        name="api_project_generate_file",
    ),
    path(
        "api/project/<int:project_id>/generate_file/",
        views.DownloadExcelFile.as_view(),
        name="api_project_category_generate_file",
    ),
    path(
        "api/generate_file/",
        views.DownloadExcelFile.as_view(),
        name="api_generate_file",
    ),
    path(
        "api/project/<int:project_id>/category/<int:category_id>/tables/",
        views.GetTableData.as_view(),
        name="api_project_category_tables",
    ),
    path(
        "project/<slug:project_slug>/category/<slug:category_slug>/tables/",
        views.project_category_tables,
        name="project_category_tables",
    ),
    path("generated_files/", views.generated_files_list, name="generated_files_list"),
    path(
        "delete_generated_file/<int:file_id>",
        views.delete_generated_file,
        name="delete_generated_file",
    ),
    path("upload_data/", views.upload_data_page, name="upload_data_page"),
    path("api/upload_chunks/", views.upload_chunks, name="upload_chunks"),
]
