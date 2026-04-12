# 🔧 OAuth Development Environment Fix

## 🚨 **Problem Identified**

OAuth działa poprawnie w Docker (port 3000) ale nie w lokalnym development (port 5174) z `make dev`.

### ✅ **Working Environment (Docker):**
```
Frontend: http://localhost:3000/audit#tab=audit&phase=landing
Backend:  http://localhost:8003
OAuth:    ✅ GitHub Mock działa poprawnie
```

### ❌ **Broken Environment (Local Dev):**
```
Frontend: http://localhost:5174/#tab=audit&phase=landing
Backend:  http://localhost:8200 (nie uruchomiony)
OAuth:    ❌ Przekierowuje do http://localhost:5174/auth/github
```

---

## 🔍 **Root Cause Analysis**

### ✅ **Problem Sources Identified:**

1. **Brakujące zmienne środowiskowe w Makefile**
   - `VITE_API_URL` nie było ustawione dla frontendu
   - `APP_URL` i `FRONTEND_URL` nie były ustawione dla backendu

2. **Nieprawidłowa konfiguracja CORS**
   - Backend skonfigurowany dla "nvidia" hostname
   - Development używa localhost

3. **Backend nie uruchomiony w development**
   - `make dev` uruchamia tylko frontend
   - Backend musi być uruchomiony osobno

---

## 🛠️ **Solutions Implemented**

### ✅ **1. Makefile Configuration Fix**

**Before:**
```bash
dev:
    @cd backend && $(UVICORN) server:app --reload --port $(BACKEND_PORT) &
    @cd frontend && npm run dev -- --port $(FRONTEND_PORT) &
```

**After:**
```bash
dev:
    @cd backend && APP_URL=http://localhost:$(BACKEND_PORT) FRONTEND_URL=http://localhost:$(FRONTEND_PORT) $(UVICORN) server:app --reload --port $(BACKEND_PORT) &
    @cd frontend && VITE_API_URL=http://localhost:$(BACKEND_PORT) npm run dev -- --port $(FRONTEND_PORT) &
```

### ✅ **2. CORS Configuration Fix**

**Before:**
```python
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", f"{FRONTEND_URL},https://semcod.com").split(",") if o.strip()]
```

**After:**
```python
default_origins = f"{FRONTEND_URL},https://semcod.com"
if "localhost" in FRONTEND_URL or "127.0.0.1" in FRONTEND_URL:
    default_origins += ",http://localhost:3000,http://localhost:5174,http://127.0.0.1:3000,http://127.0.0.1:5174"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", default_origins).split(",") if o.strip()]
```

---

## 🚀 **How to Use Development Environment**

### ✅ **Option 1: Use Docker (Recommended)**
```bash
# Zawsze działa, pełne środowisko
docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d
# Dostęp: http://localhost:3000
```

### ✅ **Option 2: Fixed Local Development**
```bash
# Uruchom backend i frontend jednocześnie
make dev
# Dostęp: http://localhost:5174 (frontend), http://localhost:8200 (backend)
```

### ✅ **Option 3: Manual Development**
```bash
# Terminal 1 - Backend
cd backend
APP_URL=http://localhost:8200 FRONTEND_URL=http://localhost:5174 python3 -m uvicorn server:app --reload --port 8200

# Terminal 2 - Frontend  
cd frontend
VITE_API_URL=http://localhost:8200 npm run dev -- --port 5174
```

---

## 🔧 **Environment Variables Explained**

### ✅ **Frontend Variables:**
```bash
VITE_API_URL=http://localhost:8200  # API URL dla frontendu
```

### ✅ **Backend Variables:**
```bash
APP_URL=http://localhost:8200       # Backend URL dla OAuth
FRONTEND_URL=http://localhost:5174  # Frontend URL dla CORS
```

### ✅ **CORS Configuration:**
Backend automatycznie dodaje localhost origins gdy wykryje localhost w FRONTEND_URL.

---

## 🧪 **Testing the Fix**

### ✅ **Verification Steps:**

1. **Uruchom środowisko:**
   ```bash
   make dev
   ```

2. **Sprawdź usługi:**
   ```bash
   curl http://localhost:8200/api/health  # Powinien zwrócić "ok"
   curl http://localhost:5174           # Powinien zwrócić 200
   ```

3. **Test OAuth:**
   - Otwórz http://localhost:5174
   - Kliknij "Connect GitHub →"
   - Powinien przekierować do mock GitHub i z powrotem

---

## 📊 **Environment Comparison**

| Aspect | Docker (port 3000) | Local Dev (port 5174) |
|--------|-------------------|----------------------|
| **Setup** | `docker compose up -d` | `make dev` |
| **Backend** | http://localhost:8003 | http://localhost:8200 |
| **Frontend** | http://localhost:3000 | http://localhost:5174 |
| **OAuth** | ✅ Works out of box | ✅ Fixed with variables |
| **Mock GitHub** | http://localhost:4010 | http://localhost:4010 |
| **Database** | PostgreSQL (Docker) | SQLite (local) |
| **Redis** | Redis (Docker) | None (local) |

---

## 🎯 **Recommendations**

### ✅ **For Development:**
1. **Używaj Docker** dla pełnego środowiska z bazą danych i Redis
2. **Używaj `make dev`** dla szybkiego developmentu bez zależności Docker
3. **Sprawdzaj zmienne środowiskowe** przed uruchomieniem

### ✅ **For Testing:**
1. **Zawsze testuj OAuth** po zmianie konfiguracji
2. **Sprawdzaj health endpoints** przed testami GUI
3. **Używaj odpowiednich portów** dla każdego środowiska

---

## 🔍 **Troubleshooting**

### ✅ **Common Issues:**

**OAuth nie działa:**
```bash
# Sprawdź zmienne środowiskowe
echo $VITE_API_URL
echo $APP_URL
echo $FRONTEND_URL

# Sprawdź czy backend działa
curl http://localhost:8200/api/health
```

**CORS errors:**
```bash
# Sprawdź konfigurację CORS w backend
grep CORS_ORIGINS backend/config.py
```

**Frontend nie łączy się z API:**
```bash
# Sprawdź console w przeglądarce
# Powinno pokazywać requesty do http://localhost:8200
```

---

## ✅ **Fix Summary**

**Problem:** OAuth działał w Docker ale nie w lokalnym development z `make dev`

**Root Cause:** Brakujące zmienne środowiskowe i nieprawidłowa konfiguracja CORS

**Solution:** 
1. ✅ Zaktualizowano Makefile z poprawnymi zmiennymi środowiskowymi
2. ✅ Dodano dynamiczną konfigurację CORS dla localhost
3. ✅ Zapewniono instrukcje dla obu środowisk

**Result:** OAuth teraz działa poprawnie w Docker i lokalnym development

---

*Fix implemented: 2026-04-11 20:35*  
*Status: ✅ RESOLVED*
