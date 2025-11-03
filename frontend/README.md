# ParagonAI Dashboard

A Next.js-powered GenAI agent deployment dashboard with a modern Neo-Synth theme.

## Features

- 🚀 **Landing Page** with animated terminal mockup
- 📊 **Dashboard** with active deployments, activity feed, and metrics
- 📈 **Detailed Metrics** with charts and deployment timeline
- 🗂️ **Project Explorer** with file tree and code preview
- 📦 **Deployments** management page
- 👤 **Account Settings** with profile and CLI credentials
- ℹ️ **About Us** page

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **TailwindCSS** with custom Neo-Synth theme
- **Recharts** for data visualization
- **Lucide React** for icons

## Color Palette

- **Primary**: `#060606` (Black Canvas)
- **Accent**: `#7C3AED` (Vivid Purple)
- **Secondary**: `#EC4899` (vivid Magenta)
- **Highlight**: `#FACC15` (Soft Yellow Spark)
- **Text**: `#E5E7EB` (Soft Gray)

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── metrics/
│   ├── account/
│   ├── about/
│   ├── dashboard/
│   ├── deployments/
│   ├── explorer/
│   ├── metrics/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── Navigation.tsx
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## API Integration

The dashboard includes a placeholder API route at `/api/metrics`. Connect this to your backend API to fetch real metrics data.

## License

MIT

