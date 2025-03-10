from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Student(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group, related_name="student_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="student_permissions", blank=True)

class Professor(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)

class Module(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)

class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField(choices=[(1, "1"), (2, "2")])

    class Meta:
        unique_together = ("module", "year", "semester")

class ProfessorModuleInstance(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("professor", "module_instance")

class Rating(models.Model):
    professor_module_instance = models.ForeignKey(ProfessorModuleInstance, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("student", "professor_module_instance")
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name="rating_between_1_and_5")
        ]

