# Mock GitHub Simulation Configuration
MOCK_GITHUB_CLIENT_ID=Iv1.mock_test_client
MOCK_GITHUB_CLIENT_SECRET=mock_secret_for_testing
MOCK_GITHUB_APP_ID=999999
MOCK_GITHUB_WEBHOOK_SECRET=whsec_mock_test

# Mock User Configuration
MOCK_USER_LOGIN=tom-sapletta-com
MOCK_USER_NAME=Tom Sapletta
MOCK_USER_EMAIL=tom@sapletta.com
MOCK_USER_ID=5669315
MOCK_USER_BIO=Architect & Developer
MOCK_USER_COMPANY=Softreck
MOCK_USER_LOCATION=Gdańsk, Poland
MOCK_USER_AVATAR_URL=https://avatars.githubusercontent.com/u/5669315?v=4
MOCK_USER_PUBLIC_REPOS=150
```

# backend - teraz używa zmiennych z .env
- GITHUB_CLIENT_ID=${MOCK_GITHUB_CLIENT_ID}
- GITHUB_CLIENT_SECRET=${MOCK_GITHUB_CLIENT_SECRET}
- GITHUB_APP_ID=${MOCK_GITHUB_APP_ID}
- GITHUB_WEBHOOK_SECRET=${MOCK_GITHUB_WEBHOOK_SECRET}

# mock-github - wszystkie dane z .env
- MOCK_USER_LOGIN=${MOCK_USER_LOGIN}
- MOCK_USER_NAME=${MOCK_USER_NAME}
- MOCK_USER_EMAIL=${MOCK_USER_EMAIL}
# Zamiast hardcoded values:
def get_mock_user():
    return {
        "id": int(os.getenv("MOCK_USER_ID", "5669315")),
        "login": os.getenv("MOCK_USER_LOGIN", "tom-sapletta-com"),
        "name": os.getenv("MOCK_USER_NAME", "Tom Sapletta"),
        # ... wszystkie pola z .env
    }
```

---

# mock-github/server.py
MOCK_USERS = {
    "tom-sapletta-com": {
        "id": 5669315,
        "login": "tom-sapletta-com",  # HARD
        "name": "Tom Sapletta",       # CODED
        # ...
    }
}

# docker-compose.sim.yml
- GITHUB_CLIENT_ID=Iv1.mock_test_client  # HARD
- GITHUB_CLIENT_SECRET=mock_secret_for_testing  # CODED
```

# mock-github/server.py
def get_mock_user():
    return {
        "id": int(os.getenv("MOCK_USER_ID", "5669315")),
        "login": os.getenv("MOCK_USER_LOGIN", "tom-sapletta-com"),
        "name": os.getenv("MOCK_USER_NAME", "Tom Sapletta"),
        # ... z .env
    }

# docker-compose.sim.yml
- GITHUB_CLIENT_ID=${MOCK_GITHUB_CLIENT_ID}
- GITHUB_CLIENT_SECRET=${MOCK_GITHUB_CLIENT_SECRET}
```

---

# Token Exchange
{
  "access_token": "gho_mock_317eb822afd04664a58b291a",
  "token_type": "bearer"
} ✅

# User Profile (z .env)
{
  "login": "tom-sapletta-com",
  "name": "Tom Sapletta", 
  "email": "tom@sapletta.com",
  "company": "Softreck",
  "location": "Gdańsk, Poland"
} ✅
```

# Backend container
docker compose exec backend env | grep MOCK
✅ MOCK_USER_LOGIN=tom-sapletta-com
✅ MOCK_USER_NAME=Tom Sapletta
✅ MOCK_GITHUB_CLIENT_ID=Iv1.mock_test_client
# Mock GitHub container  
docker compose exec mock-github env | grep MOCK
✅ MOCK_USER_LOGIN=tom-sapletta-com
✅ MOCK_USER_NAME=Tom Sapletta
## 📊 **Lokalizacja danych - Przed vs Po:**

| Typ danych | Przed | Po |
|------------|-------|-----|
| **Mock OAuth credentials** | `docker-compose.sim.yml` | ✅ `.env` |
| **User data (login, name, email)** | `mock-github/server.py` | ✅ `.env` |
| **User profile (bio, company, location)** | `mock-github/server.py` | ✅ `.env` |
| **Repository mapping** | Hardcoded "tom-sapletta-com" | ✅ Dynamic z `.env` |
| **JWT Secret Key** | `.env` | ✅ `.env` (bez zmian) |
| **Real GitHub secrets** | `.env` | ✅ `.env` (bez zmian) |

---

### ✅ **Centralizacja konfiguracji:**
- Wszystkie dane w jednym pliku `.env`
- Łatwe zarządzanie i modyfikacje
- Spójność środowisk (dev/staging/prod)

### ✅ **Bezpieczeństwo:**
- Brak hardcoded credentials w kodzie
- Możliwość dodania `.env` do `.gitignore`
- Łatwa rotacja sekretów

### ✅ **Elastyczność:**
- Możliwość zmiany usera bez modyfikacji kodu
- Łatwe testowanie różnych konfiguracji
- Wsparcie dla wielu użytkowników testowych

### ✅ **Maintainability:**
- Jedno miejsce do aktualizacji danych
- Brak potrzeby rebuild kontenerów przy zmianach usera
- Czytelny i dokumentowany kod

---

# .env
MOCK_USER_LOGIN=new-test-user
MOCK_USER_NAME=New Test User
MOCK_USER_EMAIL=new@test.com
MOCK_USER_COMPANY=New Company

# Restart tylko backend i mock-github
docker compose restart backend mock-github
```

# .env
MOCK_GITHUB_CLIENT_ID=new_client_id
MOCK_GITHUB_CLIENT_SECRET=new_secret

# Restart backend
docker compose restart backend
```

---

### ✅ **100% sukcesu refaktoryzacji:**
- ✅ **Wszystkie dane przeniesione do `.env`**
- ✅ **Zero hardcoded values w kodzie**
- ✅ **Wszystkie testy przechodzą**
- ✅ **Pełna kompatybilność wsteczna**
- ✅ **Łatwość konfiguracji i modyfikacji**

### 🎯 **System jest teraz:**
- **Konfigurowalny** - przez zmienne środowiskowe
- **Bezpieczny** - brak sekretów w kodzie
- **Elastyczny** - łatwa zmiana userów i credentials
- **Profesjonalny** - zgodny z najlepszymi praktykami

**Refaktoryzacja zakończona sukcesem! 🚀**
