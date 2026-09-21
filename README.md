# CampusHire

> A full-stack campus recruitment management platform that digitizes the recruitment lifecycle from student eligibility and job applications to interviews, selection, and offers.

## Overview

CampusHire is a role-based campus recruitment management platform designed for colleges, students, recruiters, and Training & Placement (TPO) administrators.

The system centralizes student profiles, academic information, skills, resumes, company and recruiter information, job postings, eligibility criteria, applications, interviews, and recruitment workflows behind a secure REST API.

The backend is built with **Django REST Framework** and **PostgreSQL**, with **JWT authentication** and role-based access control. A **React.js** frontend is being developed as the client application, and the project is being prepared for **Docker-based containerization and deployment**.

> **Current scope:** The repository is actively developed. Features marked as planned or in development in this README will be updated as they are completed.

---

## Objectives

CampusHire aims to:

- Centralize campus recruitment data and workflows
- Provide secure role-based access for Students, Recruiters, and TPO/Admin users
- Automate candidate eligibility evaluation
- Manage job applications through controlled recruitment stages
- Support interview scheduling and tracking
- Manage selection and offer workflows
- Expose reusable REST APIs for web clients and other consumers
- Provide API documentation through OpenAPI/Swagger
- Support reproducible development and deployment through Docker

---

## Core Features

### Authentication & Authorization

- Custom Django user model
- Email-based authentication
- JWT access and refresh tokens
- Role-based access control
- Student, Recruiter, and Admin/TPO roles
- Protected REST API endpoints

### Student Management

Students can maintain:

- Personal profile
- Academic information
- Education history
- Projects
- Work experience
- Technical skills
- Resume versions

### Resume Management

- Upload resumes
- Maintain multiple resume versions
- Activate a specific resume
- Use the active resume while applying
- Validate resume ownership

### Company & Recruiter Management

- Company profiles
- Recruiter profiles
- Company-recruiter relationships
- Recruiter-specific access to job and applicant data

### Job Management

Job postings support:

- Job title and description
- Company association
- Application deadline
- Job status
- Eligibility requirements
- Required technical skills
- Required skill proficiency

### Automated Eligibility Evaluation

CampusHire evaluates candidates using:

- Minimum CGPA
- Maximum allowed backlogs
- Graduation year
- Allowed departments
- Required skills
- Required skill proficiency

The eligibility workflow provides a structured way to replace repetitive manual checks with a consistent backend validation process.

```text
Student Profile
      |
      +-- CGPA
      +-- Backlogs
      +-- Department
      +-- Graduation Year
      +-- Skills
              |
              v
       Eligibility Engine
              |
        +-----+-----+
        |           |
        v           v
     Eligible   Not Eligible
```

### Application Management

Applications follow a controlled state machine:

```text
APPLIED
   |
   +--> UNDER_REVIEW
           |
           +--> SHORTLISTED
           |       |
           |       +--> INTERVIEW
           |               |
           |               +--> SELECTED
           |                       |
           |                       +--> OFFERED
           |                              |
           |                              +--> OFFER_ACCEPTED
           |                              |
           |                              +--> OFFER_DECLINED
           |
           +--> REJECTED
   |
   +--> REJECTED
```

Application status transitions are validated by the backend instead of allowing arbitrary state changes.

### Interview Management

The interview module supports:

- Interview scheduling
- Online interviews
- Offline interviews
- Interview rescheduling
- Interviewer information
- Meeting links
- Interview locations
- Interview notes
- Interview status tracking
- Interview results and feedback

Interview lifecycle:

```text
SCHEDULED
    |
    +--> COMPLETED
    |
    +--> CANCELLED
```

### REST APIs

The backend provides REST endpoints for the major recruitment domains, including:

- Authentication
- Student profiles
- Education
- Projects
- Experience
- Skills
- Resumes
- Companies
- Recruiters
- Jobs
- Eligibility
- Applications
- Interviews

Additional recruitment modules will be added as development progresses.

---

## Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- SimpleJWT

### Frontend

- React.js
- JavaScript
- REST API integration

### Database

- PostgreSQL

### API & Development

- REST APIs
- Postman
- Git
- GitHub

### API Documentation

- OpenAPI
- Swagger UI
- ReDoc

### DevOps

- Docker
- Docker Compose

---

## Architecture

```text
                         CampusHire
                             |
                +------------+------------+
                |                         |
             React.js                 REST API Clients
                |                         |
                +------------+------------+
                             |
                             v
                  Django REST Framework
                             |
              +--------------+--------------+
              |              |              |
             JWT            RBAC       Business Logic
              |              |              |
              +--------------+--------------+
                             |
                             v
                         PostgreSQL
```

The final containerized architecture is intended to use:

```text
Docker Compose
|
+-- Django REST API
|
+-- React Frontend
|
+-- PostgreSQL
```

---

## Role-Based Access

### Student

Students can:

- Manage their profile
- Add education
- Add projects
- Add experience
- Manage technical skills
- Upload and manage resumes
- Browse jobs
- Check eligibility
- Apply for eligible jobs
- Track applications
- View interviews
- View recruitment outcomes

### Recruiter

Recruiters can:

- Manage recruiter information
- Manage company information
- Create job postings
- Define eligibility criteria
- Define required skills
- View applicants for their jobs
- View interviews associated with their jobs

### TPO / Admin

TPO/Admin users can:

- Manage recruitment workflows
- Review and update application stages
- Shortlist candidates
- Schedule interviews
- Manage interview status
- Manage recruitment stages
- Manage offers
- Access administrative recruitment information

---

## Security & Data Integrity

CampusHire uses backend validation and access control for important recruitment operations.

Implemented security and integrity mechanisms include:

- JWT authentication
- Role-based authorization
- Protected API endpoints
- Ownership-based access control
- Foreign-key relationships
- Unique student-job application constraint
- Resume ownership validation
- Active resume validation
- Job deadline validation
- Eligibility validation
- Controlled application status transitions
- Controlled interview status transitions

---

## Database Design

PostgreSQL is used as the primary relational database.

Major entities include:

```text
User
 |
 +-- StudentProfile
 |      |
 |      +-- Education
 |      +-- Project
 |      +-- Experience
 |      +-- Resume
 |      +-- StudentSkill
 |
 +-- RecruiterProfile
        |
        +-- Company
               |
               +-- Job
                     |
                     +-- JobEligibility
                     +-- JobRequiredSkill

Application
 |
 +-- Student
 +-- Job
 +-- Resume
 |
 +-- Interview
```

The relational model uses foreign keys, uniqueness constraints, and application-level validation to maintain consistency.

---

## API Documentation

The project uses **OpenAPI-compatible API documentation** through the Django REST Framework ecosystem.

Planned documentation interfaces include:

- Swagger UI
- ReDoc
- OpenAPI schema

Swagger UI will provide an interactive interface for exploring and testing documented API endpoints.

---

## API Testing

Postman is used during backend development and API validation.

Testing covers areas such as:

- Authentication
- JWT token handling
- Role-based authorization
- CRUD operations
- Eligibility validation
- Application workflows
- Interview workflows
- Validation errors
- Permission errors
- State transitions

A dedicated automated test suite will be expanded as the project progresses.

---

## Docker & Deployment

The project is being prepared for containerized execution using Docker and Docker Compose.

Target services:

```text
Docker Compose
|
+-- Backend
|     Django REST Framework
|
+-- Frontend
|     React.js
|
+-- Database
      PostgreSQL
```

Target local startup:

```bash
docker compose up --build
```

Deployment configuration will be documented after the containerized application is finalized and tested.

---

## Project Structure

```text
CampusHire/
|
+-- backend/
|   +-- accounts/
|   +-- students/
|   +-- skills/
|   +-- companies/
|   +-- jobs/
|   +-- applications/
|   +-- config/
|   +-- manage.py
|   +-- requirements.txt
|
+-- frontend/
|   +-- src/
|   +-- public/
|   +-- package.json
|
+-- docs/
|
+-- .gitignore
+-- README.md
+-- LICENSE
```

The structure may evolve as additional backend modules, frontend functionality, testing, documentation, and deployment configuration are added.

---

## Local Development

### Prerequisites

Install:

- Python 3
- PostgreSQL
- Node.js and npm
- Git

Docker can be used once the containerization setup is complete.

### Backend Setup

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a local `.env` file and configure the database and Django settings.

Run migrations:

```bash
cd backend
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The development API will be available at:

```text
http://127.0.0.1:8000/
```

### Frontend

Frontend setup and API integration instructions will be documented as the React client is finalized.

---

## Environment Variables

Environment-specific configuration should be stored in a local `.env` file.

Example:

```env
DEBUG=True
SECRET_KEY=your-development-secret-key

DB_NAME=campushire
DB_USER=campushire_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432
```

**Never commit real credentials, secret keys, tokens, or other sensitive configuration to GitHub.**

A sanitized `.env.example` file can be used to document the required variables.

---

## Development Status

| Component | Status |
|---|---|
| Django backend | In Development |
| Custom User & JWT | Completed |
| Role-based access control | Completed |
| Student management | Completed |
| Skills management | Completed |
| Resume management | Completed |
| Company management | Completed |
| Recruiter management | Completed |
| Job management | Completed |
| Eligibility engine | Completed |
| Application workflow | Completed |
| Interview management | In Development |
| Offer management | Planned |
| TPO/Admin APIs | In Development |
| Dashboard & statistics | Planned |
| Swagger/OpenAPI | Planned |
| Automated testing | Planned |
| Docker | Planned |
| Deployment | Planned |
| React frontend | In Development |

This table will be updated as each module is completed.

---

## Recruitment Workflow

The intended end-to-end workflow is:

```text
Student Profile
       |
       v
Skills & Resume
       |
       v
Job Discovery
       |
       v
Eligibility Evaluation
       |
       v
Application
       |
       v
TPO Review
       |
       v
Shortlisting
       |
       v
Interview
       |
       v
Selection
       |
       v
Offer
       |
       v
Acceptance / Decline
```

The project focuses on backend engineering, REST API design, relational database modeling, authentication, authorization, workflow validation, containerization, and deployment.

---

## Future Scope

Planned areas include:

- Offer management
- TPO dashboards and recruitment statistics
- Expanded automated test coverage
- OpenAPI/Swagger documentation
- React frontend completion
- Docker Compose production configuration
- Deployment
- CI/CD
- Monitoring and production hardening

---

## License

CampusHire is distributed under the MIT License. See the [`LICENSE`](LICENSE) file for details.
