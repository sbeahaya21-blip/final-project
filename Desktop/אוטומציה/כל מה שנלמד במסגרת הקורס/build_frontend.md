# Building a Next.js Frontend for InvParser API

## Overview

In this tutorial, you'll build a modern, interactive frontend application for the InvParser API using **Next.js** and **GitHub Copilot**.


## Create a new GitHub repository

1. Go to [GitHub](https://github.com) and create a **new repository**
2. Name it something like `invparser-frontend` or `invoice-parser-ui`
3. Click **Create repository**
4. Clone the repository to your local machine and open it in VS Code


## Create your Copilot prompt

Create a file called `APP_PROMPT.md` in the root of your repository and paste the following prompt:

> [!IMPORTANT]
> Your app should work to some extent, not perfectly! We even prefer having some bugs as the goal is to perform UI testing later on.

```markdown
# Build a Next.js Invoice Parser Frontend

## Project Overview

Build a modern, Next.js application that serves as a frontend for an Invoice Parser API. The application should allow users to upload invoice documents and view extracted details.

## API Endpoint

The backend API is available at: `http://localhost:8082`

Current available endpoints:
- POST `/extract` - Upload an invoice file (multipart/form-data) and extract invoice details
- GET `/invoice/{invoice_id}` - Get details of a specific invoice by InvoiceId
- GET `/invoices/vendor/{vendor_name}` - Get invoices filtered by vendor name

## Technical Requirements

### Framework & Setup

- Use **Next.js** with App Router
- Use **TypeScript** for type safety
- Use **Tailwind CSS** for styling
- Use some UI library for components

### Pages & Navigation (Multi-Page Application)

Create the following pages with proper routing:

1. **Login Page** (`/login`)
   - Simple form with username and password fields
   - Dummy authentication: username: `admin`, password: `admin`
   - Store auth state in localStorage or session
   - Redirect to dashboard on successful login
   - **No real backend authentication needed** - this is just for UI testing demonstration

2. **Dashboard** (`/dashboard`)
   - Overview with statistics cards (e.g., total invoices, recent uploads)
   - Quick actions section
   - Navigation menu to other pages

3. **Upload Invoice Page** (`/upload`)
   - File upload area (drag-and-drop support)
   - File format validation (PDF, images)
   - Upload progress indicator with loading spinner
   - Success/error notifications

4. **Invoices List Page** (`/invoices`)
   - Table/grid view of all uploaded invoices
   - Filtering options (dropdown menus for status, date range)
   - Sorting capabilities
   - Pagination or infinite scroll (lazy loading)
   - Click on invoice to view details

5. **Invoice Details Page** (`/invoice/[id]`)
   - Display extracted invoice information
   - Editable fields with form validation
   - Download invoice option
   - Back navigation


### Styling Guidelines

TBD by you! go wild! 
```
