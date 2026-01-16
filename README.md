# 📊 Presentation Tools

An AI-powered presentation generator and manager that creates professional presentations from raw content, with speaker script generation.

## ✨ Features

### 📝 Presentation Generation
- Generate complete presentations from raw content using Groq AI
- Automatic content chunking for long content
- Multiple presentation templates (Rose Elegance, Warm Blue, Warm Spectrum)
- Customizable slide styles and layouts

### 🎤 Speaker Script Generation
- AI-powered professional speaker scripts
- Natural, human-like language patterns
- Automatic timing calculation per slide
- Key points and speaking notes included
- Smooth transitions between slides

### 🎨 Customization
- Multiple slide ratios (16:9, 4:3, 1:1, 2:3)
- Various bullet styles (Numbered, Elegant, Modern, Professional)
- Font selection for titles, headings, and content
- Subject-specific templates (General, Science, Engineering, Medical, IT, etc.)

### 📥 Import/Export
- Create presentations from scratch
- Download presentations as PPTX files
- Edit slides and regenerate content
- Save and manage multiple presentations

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 14+
- Groq API Key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
GROQ_API_KEY=your_api_key_here
DEBUG=False
```

Run migrations and start server:
```bash
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
.
├── backend/
│   ├── presentation_app/          # Django app
│   │   ├── models.py              # Database models
│   │   ├── views.py               # API endpoints
│   │   ├── serializers.py         # Request/response serializers
│   │   ├── presentation_generator.py  # AI content generation
│   │   ├── script_generator.py    # Speaker script generation
│   │   ├── pptx_generator.py      # PPTX export
│   │   └── templates/             # Presentation templates
│   ├── presentation_project/      # Django settings
│   ├── tests/                     # Test files
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ScriptGenerationModal.js
│   │   ├── pages/
│   │   │   ├── Home.js
│   │   │   ├── CreatePresentation.js
│   │   │   ├── PresentationDetail.js
│   │   │   └── PresentationList.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.js
│   ├── package.json
│   └── public/
├── docker-compose.yml
└── README.md
```

## 🎯 Usage

### Create a Presentation

1. Go to "Create Presentation" page
2. Enter presentation details:
   - Topic
   - Raw content
   - Target audience
   - Presentation tone
   - Number of slides (optional)
3. Select customization options:
   - Template
   - Slide ratio
   - Bullet style
   - Fonts
4. Click "Generate"

### Generate Speaker Scripts

1. Open a presentation
2. Click "🎤 Generate Script" button
3. Enter total presentation duration
4. Click "Generate Scripts"
5. View, copy, or download scripts

### Download Presentation

1. Open presentation detail
2. Select slide ratio
3. Click "Download PPTX"
4. Open in PowerPoint or compatible software

## 🔧 API Endpoints

### Presentations
- `POST /api/presentations/` - Create presentation
- `POST /api/presentations/generate/` - Generate from content
- `GET /api/presentations/` - List presentations
- `GET /api/presentations/{id}/` - Get presentation
- `PUT /api/presentations/{id}/` - Update presentation
- `DELETE /api/presentations/{id}/` - Delete presentation
- `POST /api/presentations/{id}/publish/` - Publish presentation
- `POST /api/presentations/{id}/generate_script/` - Generate scripts
- `GET /api/presentations/{id}/export_pptx/` - Export as PPTX

### Slides
- `GET /api/slides/` - List slides
- `GET /api/slides/{id}/` - Get slide
- `PUT /api/slides/{id}/` - Update slide
- `DELETE /api/slides/{id}/` - Delete slide

## 🌐 Deployment

### With Render

1. Push code to GitHub
2. Create Render account
3. New > Web Service
4. Connect GitHub repository
5. Configure environment variables
6. Deploy

### With Docker

```bash
docker-compose up
```

### Environment Variables

```env
GROQ_API_KEY=your_groq_api_key
DEBUG=False
SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=your_database_url
```

## 📦 Technologies Used

### Backend
- Django 4.2
- Django REST Framework
- Groq API (LLM)
- python-pptx
- PostgreSQL/SQLite

### Frontend
- React 18
- Ant Design
- Axios
- React Router

## 🧪 Testing

Test files are located in `backend/tests/`:

```bash
cd backend
python manage.py test
```

## 📝 Features Breakdown

### Content Generation
- Groq LLM integration
- Intelligent content chunking (300+ words)
- JSON structure validation
- Multiple slide type support

### Script Generation
- Natural language processing
- Timing calculations
- Tone-aware generation
- Context-aware transitions

### PPTX Export
- Multiple templates
- Custom fonts
- Professional styling
- Slide ratio support

## 🐛 Troubleshooting

### API Key Issues
- Verify GROQ_API_KEY is set in .env
- Check API key is valid on Groq console

### PPTX Export Fails
- Ensure all slide content is valid
- Check available disk space
- Verify python-pptx is installed

### Frontend Build Issues
- Clear node_modules: `rm -rf node_modules`
- Reinstall: `npm install`
- Clear cache: `npm cache clean --force`

## 📚 Documentation

Detailed documentation available in individual component files.

## 📄 License

Your License Here

## 👥 Support

For issues and questions, please open an issue on GitHub.

## 🎉 Credits

Built with ❤️ using Django, React, and Groq AI
