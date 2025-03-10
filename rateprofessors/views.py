from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg
from django.db import IntegrityError
from .models import Professor, Module, ModuleInstance, ProfessorModuleInstance, Rating

Student = get_user_model()

class MyView(APIView):
    def get(self, request):
        return Response("Success!")

class RegisterStudent(APIView):
    def post(self, request):
        username = request.data.get('username').strip().lower()
        email = request.data.get('email').strip().lower()
        password = request.data.get('password')
        if not all([username, email, password]):
            return Response("All fields are required", status=400)
        try:
            Student.objects.create_user(username=username, email=email, password=password)
            return Response("User created", status=201)
        except IntegrityError:
            return Response("Username or email already exists. Please choose a different one", status=400)

class LoginStudent(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not all([username, password]):
            return Response("Username and password are required", status=400)
        student = authenticate(username=username, password=password)
        if student:
            token = RefreshToken.for_user(student)
            return Response(str(token.access_token))
        return Response("Invalid credentials. Please try again", status=400)

class ModuleList(APIView):
    def get(self, request):
        try:
            module_instances = ModuleInstance.objects.prefetch_related('professormoduleinstance_set__professor').select_related('module')
            data = []
            for module_instance in module_instances:
                professors = module_instance.professormoduleinstance_set.all()
                professor_list = [f"{p.professor.id}, Professor {p.professor.name}" for p in professors]
                data.append({
                    "code": module_instance.module.code,
                    "name": module_instance.module.name,
                    "year": module_instance.year,
                    "semester": module_instance.semester,
                    "taught_by": professor_list if professor_list else "No assigned professors"
                })
            return Response(data)
        except Exception:
            return Response("An unknown error occurred. Please try again later.", status=500)

class ProfessorRatings(APIView):
    def get(self, request):
        professor_id = request.query_params.get('professor_id')
        module_code = request.query_params.get('module_code')
        try:
            if professor_id:
                Professor.objects.get(id=professor_id)
            if module_code:
                Module.objects.get(code=module_code)
            professors = Professor.objects.filter(id=professor_id) if professor_id else Professor.objects.all()
            data = []
            for professor in professors:
                ratings_query = Rating.objects.filter(professor_module_instance__professor=professor)
                if module_code:
                    ratings_query = ratings_query.filter(professor_module_instance__module_instance__module__code=module_code)
                if ratings_query.exists():
                    avg_rating = ratings_query.aggregate(avg=Avg('rating'))['avg'] or 0
                    module_instance = ratings_query.first()
                    module_code_value = module_instance.professor_module_instance.module_instance.module.code if module_instance else ""
                    module_name_value = module_instance.professor_module_instance.module_instance.module.name if module_instance else ""
                else:
                    avg_rating = 0
                    module_code_value = ""
                    module_name_value = ""
                data.append({
                    "id": professor.id,
                    "name": professor.name,
                    "rating": round(avg_rating, 1),
                    "module_code": module_code_value,
                    "module_name": module_name_value
                })
            if not data:
                return Response("No ratings found with the given parameters", status=404)
            return Response(data)
        except (Professor.DoesNotExist, Module.DoesNotExist):
            return Response("Professor or Module doesn't exist", status=404)
        except Exception:
            return Response("An unknown error occurred. Please try again later.", status=500)

class RateProfessor(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        student = request.user
        professor_id = request.data.get('professor_id')
        module_code = request.data.get('module_code')
        year = request.data.get('year')
        semester = request.data.get('semester')
        rating = request.data.get('rating')
        if any(value is None for value in [professor_id, module_code, year, semester, rating]):
            return Response("All fields are required", status=400)
        try:
            rating_int = int(rating)
            year_int = int(year)
            semester_int = int(semester)
            if rating_int < 1 or rating_int > 5:
                return Response("Rating must be between 1 and 5", status=400)
        except ValueError:
            return Response("Year, semester, and rating must be valid numbers", status=400)
        if not Professor.objects.filter(id=professor_id).exists() or not Module.objects.filter(code=module_code).exists():
            return Response("Professor or Module doesn't exist", status=404)
        instance = ProfessorModuleInstance.objects.filter(
            professor__id=professor_id,
            module_instance__module__code=module_code,
            module_instance__year=year_int,
            module_instance__semester=semester_int
        ).first()
        if not instance:
            return Response("No teaching assignment found for given professor, module, year, and semester", status=400)
        try:
            Rating.objects.update_or_create(student=student, professor_module_instance=instance, defaults={"rating": rating_int})
            return Response("Rating submitted")
        except Exception:
            return Response("An unknown error occurred. Please try again later.", status=500)
