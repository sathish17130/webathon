# CompareX AI – Intelligent Specification Comparison Engine

A full-stack Django web application that works like an e-commerce “spec comparison” tool:

- **Admin** defines categories (Laptop, Phone, Tablet, etc.)
- **Admin** defines a full set of **specification fields + weights** per category
- **Users** enter multiple items with those specs
- The system **ranks** them, highlights the best option, shows a chart, and generates an **AI explanation** (placeholder-ready)

## Features

- **Dynamic, category-specific specifications**: No hardcoded fields; every category can have its own spec set
- **Admin-defined weights**: Each numeric spec can influence scoring via a weight
- **User-entered items**: Users enter 2–5 items and their specifications in a dynamic form
- **Intelligent scoring**: Weighted scoring ranks user-entered items
- **Visual Dashboard**: Interactive charts and comparison tables using Chart.js
- **AI Explanations**: AI-generated explanation for the best option (placeholder ready for OpenAI integration)
- **Modern UI**: Clean, responsive Bootstrap-based interface

## Tech Stack

- **Backend**: Django 5.0+
- **Frontend**: HTML, CSS, Bootstrap 5
- **Charts**: Chart.js
- **Database**: SQLite
- **Architecture**: Service-layer architecture

## Installation & Setup

### 1. Install Dependencies

```bash
pip install django requests python-dotenv
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

Recommended (local dev): create a virtual environment first:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional - for admin access)

```bash
python manage.py createsuperuser
```

### 4. Add Sample Data

**Option 1: Using the sample data script (Recommended)**

```bash
python manage.py shell < add_sample_data.py
```

This will create sample categories and **specification fields** automatically.

**Option 2: Via Django Admin**

1. Start the server: `python manage.py runserver`
2. Navigate to `http://127.0.0.1:8000/admin/`
3. Login with your superuser credentials
4. Add Categories (e.g., `Laptop`, `Phone`, `Tablet`)
5. For each category, add `SpecificationField` entries (examples):
   - Laptop: `price`, `ram`, `battery`, `performance`, `graphics`, `processor` (text)
   - Phone: `price`, `camera_score`, `battery`, `storage`, `display_score`
6. Set weights for numeric specs (e.g., price 0.4, performance 0.3, battery 0.2, graphics 0.1)

### 5. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
compare_engine/
├── manage.py
├── compare_engine/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── services/
│       ├── __init__.py
│       ├── comparison_engine.py
│       └── ai_service.py
├── templates/
│   ├── home.html
│   ├── compare.html
│   └── result.html
├── requirements.txt
└── README.md
```

## Enabling AI Explanations

Currently, the AI service uses a placeholder API key. To enable real AI explanations:

1. **Create a `.env` file** in the project root:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

2. **Update `core/services/ai_service.py`**:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   API_KEY = os.getenv('OPENAI_API_KEY')
   ```

3. The AI service will automatically use your API key for generating explanations.

## Usage

1. **Home Page**: Browse available categories
2. **Compare Page**:
   - Enter multiple items (e.g., 3 laptops)
   - Fill in the dynamic spec fields loaded from admin configuration
   - Click **“Analyze Best <Category>”**
3. **Result Page**:
   - See the best recommended item
   - View AI-generated explanation
   - Explore comparison chart
   - Review complete ranking table

## Development Notes

- Specs are stored per item in `UserItem.specifications` (JSON)
- Scoring uses admin-defined `SpecificationField.weight` for **numeric** fields:
  \[
  score = \sum (value \times weight)
  \]
- Text specs are displayed in the comparison table but do not affect score

## License

This project is created for hackathon purposes.

## Contributing

Feel free to fork and enhance this project!
