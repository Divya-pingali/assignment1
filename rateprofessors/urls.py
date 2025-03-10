from django.urls import path
from .views import ModuleList, ProfessorRatings, RegisterStudent, LoginStudent, RateProfessor

urlpatterns = [
    path('modules/', ModuleList.as_view(), name='module-list'),
    path('ratings/', ProfessorRatings.as_view(), name='professor-ratings'),
    path('register/', RegisterStudent.as_view(), name='register-student'),
    path('login/', LoginStudent.as_view(), name='login-student'),
    path('rate-professor/', RateProfessor.as_view(), name='rate-professor')
]