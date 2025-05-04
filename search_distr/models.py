import calendar
from transliterate import translit
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class Month(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    month_name = models.CharField(blank=True, null=True, max_length=250)

    def save(self, *args, **kwargs):
        if not self.month_name:
            self.month_name = calendar.month_name[self.month]
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.month_name} {self.year}"


class Region(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True, max_length=250, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.name = str(self.name)

            transliterated_name = translit(self.name, "uk", reversed=True)
            self.slug = slugify(transliterated_name)
        if "_" in self.slug:
            self.slug = self.slug.replace("_", "-")
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Settlement(models.Model):
    name = models.CharField(max_length=255)
    community = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True, max_length=250, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.name = str(self.name)
            transliterated_name = translit(self.name, "uk", reversed=True)
            self.slug = slugify(transliterated_name)

        if "_" in self.slug:
            self.slug = self.slug.replace("_", "-")
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} - {self.region.name}"


class Person(models.Model):
    GENDER_CHOICES = [
        ("M", "Male/Чоловік"),
        ("F", "Female/Жінка"),
    ]
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, default="-")
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE)
    is_idp = models.BooleanField(default=False)
    is_returnees = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Distribution(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    category = models.ForeignKey('reports.Category', blank=True, null=True, on_delete=models.CASCADE)
    is_received = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.person.name} {self.month.month_name} {self.month.year}"


class File(models.Model):
    date = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to="generated_files", null=True, blank=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

class ManagerAccess(models.Model):
    is_full = models.BooleanField(default=False)
    regions = models.ManyToManyField(Region, verbose_name="Regions", blank=True)

    def __str__(self) -> str:
        return 'Full Access' if self.is_full else f'{", ".join([r.name for r in self.regions.all()])}'
