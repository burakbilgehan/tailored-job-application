# tailored-job-application — Product Spec

**Versiyon:** 0.1 (draft)
**Durum:** Onay bekliyor

---

## 1. Problem

İş başvurularında genel bir CV ve cover letter yeterli değil. Her pozisyon farklı; adayın güçlü yanlarını o role göre çerçevelemek hem zaman alıyor hem de uzmanlık gerektiriyor. Bu araç süreci otomatize eder.

---

## 2. Kapsam

### Girdi

| Alan | Format | Zorunlu |
|---|---|---|
| CV | `.tex` (LaTeX) veya `.md` | Evet |
| Profil ek bağlamı | Serbest metin (LinkedIn about, portfolio özeti, notlar) | Hayır |
| İş ilanı | Serbest metin veya URL | Evet |
| Ek bağlam | Şirket hakkında notlar, özel vurgular isteniyor mu, ton tercihi | Hayır |

### Çıktı

1. **Cover Letter** — pozisyona özel, markdown formatında, indirilebilir
2. **CV Revizyon Önerileri** — madde madde, hangi bölüm nasıl güçlendirilmeli
3. **Revize CV** — orijinal format korunarak (LaTeX → LaTeX, .md → .md) güncellenmiş versiyon, indirilebilir

---

## 3. Kullanıcı Akışı

```
1. Kullanıcı web arayüzünü açar
2. CV dosyasını yükler (.tex veya .md)
3. Opsiyonel: ek profil bağlamı girer (plain text area)
4. İş ilanını yapıştırır (metin) veya URL girer
5. Opsiyonel: ek bağlam / ton tercihi belirtir
6. "Analiz Et" butonuna basar
7. Sonuçlar üç sekmede gösterilir:
   - Cover Letter (render + kopyala + indir)
   - CV Önerileri (madde madde liste)
   - Revize CV (diff view veya raw, indir)
```

---

## 4. Mimari

```
tailored-job-application/
├── backend/          # Python, FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   └── analyze.py
│   │   ├── services/
│   │   │   ├── llm.py        # Claude API wrapper
│   │   │   ├── parser.py     # CV parsing (LaTeX / MD)
│   │   │   └── generator.py  # output assembly
│   │   └── models/
│   │       └── schemas.py    # Pydantic models
│   ├── pyproject.toml
│   └── .env.example
├── frontend/         # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputForm/
│   │   │   ├── ResultTabs/
│   │   │   └── FileUpload/
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
└── docs/
```

---

## 5. Backend API

### `POST /api/analyze`

**Request (multipart/form-data):**

```
cv_file        : File (.tex | .md)
profile_context: string (optional)
job_listing    : string
job_url        : string (optional, alternatif)
extra_context  : string (optional)
```

**Response (JSON):**

```json
{
  "cover_letter": {
    "markdown": "...",
    "filename": "cover_letter_<timestamp>.md"
  },
  "cv_suggestions": [
    { "section": "Experience", "suggestion": "..." },
    ...
  ],
  "revised_cv": {
    "content": "...",
    "format": "latex | markdown",
    "filename": "cv_revised_<timestamp>.tex"
  }
}
```

### `GET /api/download/{filename}`

Önceden üretilmiş dosyayı indirir.

---

## 6. LLM Stratejisi

- **Model:** `claude-opus-4-6` (kalite kritik)
- **Yaklaşım:** Tek büyük prompt yerine zincir:
  1. **Analiz prompt:** CV + iş ilanı → aday güçlü yanları & gap analizi
  2. **Cover letter prompt:** analiz sonucu → cover letter
  3. **CV revizyon prompt:** analiz sonucu + orijinal CV → öneriler + revize içerik
- **Sistem prompt:** Ton ve format kısıtları burada tanımlanır

---

## 7. Açık Kararlar

> Bunları onaylamadan implementasyona geçmiyoruz.

| # | Soru | Seçenekler | Öneri |
|---|---|---|---|
| A | URL'den iş ilanı çekilsin mi? | Hayır (sadece paste) / Evet (scraping) | Evet, basit fetch |
| B | Sonuçlar kaydedilsin mi? | Session bazlı (bellekte) / Dosya sistemi / DB | Session bazlı, sade tutulsun |
| C | Auth var mı? | Yok / API key koruması | Yok (kişisel araç) |
| D | CV diff view? | Sadece raw / Yan yana diff | Yan yana diff, daha kullanışlı |
| E | Dil desteği? | Sadece İngilizce | Cikti daima ingilizce olsun, girdi turkce de olabilir ingilizce de |

---

## 8. Kapsam Dışı (v1)

- Kullanıcı hesapları / geçmiş
- Toplu başvuru işleme
- ATS skor hesaplama
- Otomatik iş ilanı arama
