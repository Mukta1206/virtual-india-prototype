# =========================================================
# ✅ SAFE, CLEAN, FULLY FUNCTIONAL VIEWS.PY (with improved live suggestions)
# =========================================================

import json
from django.views.decorators.csrf import csrf_exempt
import openai
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from internship_project.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from random import randrange
import os
import re
from django.conf import settings
from django.http import JsonResponse  # ✅ for autocomplete API
from difflib import SequenceMatcher
from unidecode import unidecode


# =========================================================
# 🌐 Core Page Views
# =========================================================

def front(request):
    if request.method == "POST":
        login(request)
        return redirect("user_login")
    else:
        return render(request, "front.html")


def user_signup(request):
    if request.method == "POST":
        un = request.POST.get("un")
        try:
            usr = User.objects.get(username=un)
            return render(request, "user_signup.html", {"msg": "email already registered"})
        except User.DoesNotExist:
            pw = ""
            text = "abcdefghijklmnopqrstuvwxyz1234567890"
            for i in range(5):
                pw += text[randrange(len(text))]

            sub = "Welcome To Your Virtual Tour Of Maharashtra"
            msg = f"Your Password is : {pw}\nNote: PLEASE CHANGE YOUR PASSWORD ONCE YOU LOGIN BY CLICKING ON FORGOT PASSWORD"
            sender = EMAIL_HOST_USER
            rvr = [str(un)]
            send_mail(sub, msg, sender, rvr)

            usr = User.objects.create_user(username=un, password=pw)
            usr.save()
            return redirect("user_login")
    else:
        return render(request, "user_signup.html")


def user_login(request):
    if request.method == "POST":
        un = request.POST.get("un")
        pw = request.POST.get("pw")
        usr = authenticate(username=un, password=pw)
        if usr is None:
            return render(request, "user_login.html", {"msg": "invalid login"})
        else:
            login(request, usr)
            return redirect("home")
    else:
        return render(request, "user_login.html")


def user_logout(request):
    logout(request)
    return redirect("front")


def user_cp(request):
    if request.method == "POST" and request.user.is_authenticated:
        un = request.user.username
        pw1 = request.POST.get("pw1")
        pw2 = request.POST.get("pw2")
        if pw1 == pw2:
            usr = User.objects.get(username=un)
            usr.set_password(pw1)
            usr.save()
            return redirect("user_login")
        else:
            return render(request, "user_signup.html", {"msg": "passwords don't match"})
    elif request.method == "GET" and request.user.is_authenticated:
        return render(request, "user_cp.html")
    else:
        return redirect("user_login")


def user_abt(request):
    if request.method == "POST":
        login(request)
        return redirect("user_abt")
    else:
        return render(request, "user_abt.html")


# =========================================================
# 🏙️ City Pages
# =========================================================
def mumbai(request): return render(request, "mumbai.html")
def pune(request): return render(request, "pune.html")
def nagpur(request): return render(request, "nagpur.html")
def thane(request): return render(request, "thane.html")
def nashik(request): return render(request, "nashik.html")
def aurangabad(request): return render(request, "aurangabad.html")
def solapur(request): return render(request, "solapur.html")
def kolhapur(request): return render(request, "kolhapur.html")
def satara(request): return render(request, "satara.html")
def wardha(request): return render(request, "wardha.html")
def ratnagiri(request): return render(request, "ratnagiri.html")
def amravati(request): return render(request, "amravati.html")


# =========================================================
# 🔍 MAIN SEARCH FUNCTION — Supports city + food/place matches
# =========================================================
def search_results(request):
    query = request.GET.get("q", "").strip().lower()

    if not query:
        return render(request, "search_results.html", {"query": "", "results": [], "count": 0})

    templates_dir = os.path.join(settings.BASE_DIR, "internapp", "templates")
    pattern = re.compile(r"<b>(.*?)</b>|<h[1-6]>(.*?)</h[1-6]>", re.IGNORECASE)
    results = []

    for root, _, files in os.walk(templates_dir):
        for file in files:
            if not file.endswith(".html"):
                continue

            # skip generic templates
            if file.lower() in ["home.html", "base.html", "search_results.html", "core.html"]:
                continue

            file_path = os.path.join(root, file)
            city_name = os.path.splitext(file)[0].title()
            city_lower = city_name.lower()

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read().lower()
                    matches = re.findall(pattern, html_content)

                    # ✅ Match with city name
                    if query in city_lower or city_lower in query:
                        results.append({
                            "city": city_name,
                            "item": f"Explore {city_name}",
                            "file_path": os.path.relpath(file_path, templates_dir),
                            "score": 1.0,

                            "anchor": city_lower.replace(" ", "-")
                        })

                    # ✅ Search all headings/bold tags
                    for m in matches:
                        name = unidecode((m[0] or m[1]).strip())
                        clean = re.sub(r"<.*?>", "", name).strip().lower()
                        clean = re.sub(r"[^a-z0-9\s]", "", clean)

                        if not clean:
                            continue

                        similarity = SequenceMatcher(
                            None, clean, query).ratio()
                        substring_match = 1 if query in clean else 0
                        word_match = any(
                            word in clean for word in query.split())
                        score = similarity + \
                            (0.3 if substring_match else 0) + \
                            (0.2 if word_match else 0)

                        if score > 0.5:
                            results.append({
                                "city": city_name,
                                "item": clean.title(),
                                "file_path": os.path.relpath(file_path, templates_dir),
                                "score": round(score, 2),

                                "anchor": clean.replace(" ", "-")
                            })

                    # ✅ Plain text fallback
                    if query in html_content:
                        results.append({
                            "city": city_name,
                            "item": f"General mention of '{query.title()}'",
                            "file_path": os.path.relpath(file_path, templates_dir),
                            "score": 0.6,

                            "anchor": query.replace(" ", "-")
                        })

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                continue

    # Deduplicate and sort
    unique_results = {f"{r['city']}|{r['item']}": r for r in results}.values()
    sorted_results = sorted(
        unique_results, key=lambda x: x["score"], reverse=True)

    return render(request, "search_results.html", {
        "query": query,
        "results": sorted_results,
        "count": len(sorted_results),
    })
# =========================================================
# ⚡ AUTOCOMPLETE API — Adds Food, City, and Topic suggestions
# =========================================================


def search_suggestions(request):
    query = request.GET.get("q", "").strip().lower()

    if not query:
        return render(request, "search_results.html", {"query": "", "results": [], "count": 0})

    templates_dir = os.path.join(settings.BASE_DIR, "internapp", "templates")
    pattern = re.compile(r"<b>(.*?)</b>|<h[1-6]>(.*?)</h[1-6]>", re.IGNORECASE)
    results = []

    for root, _, files in os.walk(templates_dir):
        for file in files:
            if not file.endswith(".html"):
                continue

            # skip generic templates
            if file.lower() in ["home.html", "base.html", "search_results.html", "core.html"]:
                continue

            file_path = os.path.join(root, file)
            city_name = os.path.splitext(file)[0].title()
            city_lower = city_name.lower()

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read().lower()
                    matches = re.findall(pattern, html_content)

                    # ✅ Match with city name
                    if query in city_lower or city_lower in query:
                        results.append({
                            "city": city_name,
                            "item": f"Explore {city_name}",
                            "file_path": os.path.relpath(file_path, templates_dir),
                            "score": 1.0,

                            "anchor": city_lower.replace(" ", "-")
                        })

                    # ✅ Search all headings/bold tags
                    for m in matches:
                        name = unidecode((m[0] or m[1]).strip())
                        clean = re.sub(r"<.*?>", "", name).strip().lower()
                        clean = re.sub(r"[^a-z0-9\s]", "", clean)

                        if not clean:
                            continue

                        similarity = SequenceMatcher(
                            None, clean, query).ratio()
                        substring_match = 1 if query in clean else 0
                        word_match = any(
                            word in clean for word in query.split())
                        score = similarity + \
                            (0.3 if substring_match else 0) + \
                            (0.2 if word_match else 0)

                        if score > 0.5:
                            results.append({
                                "city": city_name,
                                "item": clean.title(),
                                "file_path": os.path.relpath(file_path, templates_dir),
                                "score": round(score, 2),

                                "anchor": clean.replace(" ", "-")
                            })

                    # ✅ Plain text fallback
                    if query in html_content:
                        results.append({
                            "city": city_name,
                            "item": f"General mention of '{query.title()}'",
                            "file_path": os.path.relpath(file_path, templates_dir),
                            "score": 0.6,

                            "anchor": query.replace(" ", "-")
                        })

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                continue

    # Deduplicate and sort
    unique_results = {f"{r['city']}|{r['item']}": r for r in results}.values()
    sorted_results = sorted(
        unique_results, key=lambda x: x["score"], reverse=True)

    return JsonResponse({
        "query": query,
        "results": sorted_results,
        "count": len(sorted_results),
    })


openai.api_key = "YOUR_API_KEY"


@csrf_exempt
def chatgpt_response(request):
    data = json.loads(request.body)
    user_message = data.get("message", "")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant for a tourism website. Provide friendly, fact-based answers about tourist attractions, hotels, weather, routes, etc."},
                {"role": "user", "content": user_message}
            ],
        )
        reply = response.choices[0].message.content
        return JsonResponse({"reply": reply})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
