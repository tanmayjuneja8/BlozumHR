from django.db import models
from django import forms
from django.forms import ClearableFileInput

# for deleting media files after record is deleted
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Resume(models.Model):
    resume = models.FileField("Upload Resumes", upload_to="resumes/")
    name = models.CharField("Name", max_length=255, null=True, blank=True)
    contact = models.CharField("Contact", max_length=255, null=True, blank=True)
    email = models.CharField("Email", max_length=255, null=True, blank=True)
    companies = models.CharField("Companies", max_length=255, null=True, blank=True)
    college = models.CharField("College", max_length=255, null=True, blank=True)
    summary = models.CharField("Summary", max_length=1000, null=True, blank=True)
    experience = models.CharField("Experience", max_length=1000, null=True, blank=True)
    score = models.CharField("Score", max_length=1000, null=True, blank=True)
    score1 = models.IntegerField("Score1", null=True, blank=True)
    uploaded_on = models.DateTimeField("Uploaded On", auto_now_add=True)


class UploadResumeModelForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["resume"]
        widgets = {
            "resume": ClearableFileInput(attrs={"multiple": True}),
        }


# delete the resume files associated with each object or record
@receiver(post_delete, sender=Resume)
def submission_delete(sender, instance, **kwargs):
    instance.resume.delete(False)
