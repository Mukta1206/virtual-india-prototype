from django.contrib import admin
from django.urls import path
from internapp.views import home
from django.views.generic import TemplateView
# ✅ add this import (so we can use your search function)
from auapp.views import (
    user_signup, user_login, user_logout, user_cp,
    front, user_abt,
    mumbai, pune, nagpur, thane, nashik,
    aurangabad, solapur, kolhapur, satara,
    wardha, ratnagiri, amravati,
    search_results,        # ✅ already present
    search_suggestions   ,  # ✅ new import added
    chatgpt_response
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="india"),
    path("maharashtra", home, name="home"),
    path("user_signup/", user_signup, name="user_signup"),
    path("user_login/", user_login, name="user_login"),
    path("user_logout/", user_logout, name="user_logout"),
    path("user_cp/", user_cp, name="user_cp"),
    path("front/", front, name="front"),
    path("user_abt/", user_abt, name="user_abt"),
    path("mumbai/", mumbai, name="mumbai"),
    path("pune/", pune, name="pune"),
    path("nagpur/", nagpur, name="nagpur"),
    path("thane/", thane, name="thane"),
    path("nashik/", nashik, name="nashik"),
    path("aurangabad/", aurangabad, name="aurangabad"),
    path("solapur/", solapur, name="solapur"),
    path("kolhapur/", kolhapur, name="kolhapur"),
    path("satara/", satara, name="satara"),
    path("wardha/", wardha, name="wardha"),
    path("ratnagiri/", ratnagiri, name="ratnagiri"),
    path("amravati/", amravati, name="amravati"),

    # ✅ existing search route (kept same)
    path("search/", search_results, name="search_results"),

    # ⚡ new autocomplete route (used only by JS fetch, won’t affect layout)
    path("suggest/", search_suggestions, name="search_suggestions"),
    path("chatgpt/", chatgpt_response, name="chatgpt_response"),
]
