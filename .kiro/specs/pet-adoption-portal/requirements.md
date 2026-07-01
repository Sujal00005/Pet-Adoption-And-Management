# Requirements Document

## Introduction

The Pet Adoption and Rescue Management Portal is a full-stack web application that connects pets in need of adoption with potential adopters. Built as an Infosys Springboard internship project, the portal manages the complete lifecycle of pet adoption — from listing rescued animals and accepting surrender requests, to processing adoption applications and tracking their outcomes.

The system supports two user roles: **Admin** (shelter staff managing the portal) and **Adopter** (registered users browsing and applying to adopt pets). The tech stack is intentionally simple: **HTML + CSS + vanilla JavaScript** for the frontend, **Django (Python)** for the backend, and **SQLite** for the database. No external CSS frameworks or JavaScript libraries are used. The architecture is designed to be extensible for future features such as foster care, donation management, and volunteer coordination.

---

## Glossary

- **Portal**: The Pet Adoption and Rescue Management web application.
- **Admin**: A privileged user who manages pet listings, adoption applications, and user accounts.
- **Adopter**: A registered user who browses pets and submits adoption applications.
- **Pet**: An animal listed on the Portal available for adoption.
- **Pet_Profile**: A detailed page displaying all information about a specific Pet.
- **Pet_Listing**: A summary card of a Pet shown in browse/search results.
- **Adoption_Application**: A formal request submitted by an Adopter to adopt a specific Pet.
- **Application_Status**: The current state of an Adoption_Application — one of: `Pending`, `Under Review`, `Approved`, or `Rejected`.
- **Surrender_Form**: A form submitted by a member of the public to hand over a pet to the shelter.
- **Admin_Dashboard**: The administrative interface for managing all portal data.
- **Search_Filter**: A set of criteria (species, breed, age, location, gender, size) used to narrow Pet_Listing results.
- **Authentication_System**: The module responsible for user registration, login, session management, and access control.
- **Health_Status**: A pet's medical condition summary, including vaccination status and any known conditions.
- **Notification**: An in-portal or email message sent to an Adopter about their Adoption_Application status change.
- **Session**: An authenticated user's active login context, maintained via a secure token or cookie.

---

## Requirements

### Requirement 1: User Registration

**User Story:** As a visitor, I want to register as an Adopter, so that I can apply to adopt pets and track my applications.

#### Acceptance Criteria

1. THE Portal SHALL provide a registration page accessible to unauthenticated visitors.
2. WHEN a visitor submits the registration form with a unique email address, full name, phone number, and password, THE Authentication_System SHALL create a new Adopter account.
3. WHEN a visitor submits a registration form with an email address already associated with an existing account, THE Authentication_System SHALL display an error message stating the email is already registered.
4. WHEN a visitor submits a registration form with a password shorter than 8 characters, THE Authentication_System SHALL reject the submission and display a password length requirement message.
5. WHEN a visitor submits a registration form with an invalid email format, THE Authentication_System SHALL reject the submission and display an email format error.
6. THE Authentication_System SHALL hash all passwords using a secure one-way hashing algorithm before storing them in the database.
7. WHEN a new Adopter account is successfully created, THE Portal SHALL redirect the user to the login page with a success confirmation message.

---

### Requirement 2: User Login and Session Management

**User Story:** As a registered user (Admin or Adopter), I want to log in securely, so that I can access my role-specific features.

#### Acceptance Criteria

1. THE Portal SHALL provide a login page accessible to unauthenticated visitors.
2. WHEN a user submits valid credentials (email and password), THE Authentication_System SHALL create a Session and redirect the user to their role-appropriate home page.
3. WHEN a user submits an incorrect email or password, THE Authentication_System SHALL display a generic invalid credentials error without revealing which field is incorrect.
4. WHEN an authenticated Admin accesses the Portal, THE Portal SHALL display the Admin_Dashboard as the home page.
5. WHEN an authenticated Adopter accesses the Portal, THE Portal SHALL display the pet browsing page as the home page.
6. WHEN a user clicks the logout button, THE Authentication_System SHALL invalidate the Session and redirect the user to the login page.
7. WHILE a Session is active, THE Authentication_System SHALL maintain the user's authenticated state across page navigations.
8. IF a Session expires due to inactivity exceeding 60 minutes, THEN THE Authentication_System SHALL invalidate the Session and redirect the user to the login page with an expiry notice.
9. WHERE role-based access control is enforced, THE Authentication_System SHALL prevent Adopters from accessing Admin-only routes and return a 403 Forbidden response.

---

### Requirement 3: Pet Listing and Browsing

**User Story:** As an Adopter, I want to browse available pets, so that I can find a pet I want to adopt.

#### Acceptance Criteria

1. THE Portal SHALL display a browsing page showing all Pets with an `Available` adoption status.
2. WHEN the browsing page loads, THE Portal SHALL display each Pet as a Pet_Listing card containing the pet's primary photo, name, species, breed, age, and location.
3. THE Portal SHALL display Pet_Listing cards in a responsive grid layout that adapts to desktop, tablet, and mobile screen sizes.
4. WHEN no Pets with `Available` status exist in the database, THE Portal SHALL display a message indicating no pets are currently available.
5. THE Portal SHALL paginate Pet_Listing results, displaying a maximum of 12 Pet_Listing cards per page.
6. WHEN a user navigates between pages, THE Portal SHALL preserve the active Search_Filter criteria.

---

### Requirement 4: Pet Search and Filtering

**User Story:** As an Adopter, I want to filter pets by species, breed, age, and other attributes, so that I can quickly find pets that match my preferences.

#### Acceptance Criteria

1. THE Portal SHALL provide a Search_Filter panel on the pet browsing page with filter options for: species, breed, age range, gender, size, and location.
2. WHEN an Adopter applies one or more Search_Filter criteria, THE Portal SHALL update the Pet_Listing results to show only Pets matching all selected criteria.
3. WHEN an Adopter enters text in the search bar, THE Portal SHALL filter Pet_Listing results to show Pets whose name, breed, or description contains the entered text (case-insensitive).
4. WHEN an Adopter clears all Search_Filter criteria, THE Portal SHALL restore the full list of available Pet_Listing results.
5. IF no Pets match the applied Search_Filter criteria, THEN THE Portal SHALL display a message indicating no results were found and suggest clearing filters.
6. THE Portal SHALL populate the breed filter options dynamically based on the species selected in the species filter.

---

### Requirement 5: Pet Profile Page

**User Story:** As an Adopter, I want to view a detailed profile for each pet, so that I can make an informed adoption decision.

#### Acceptance Criteria

1. WHEN an Adopter clicks on a Pet_Listing card, THE Portal SHALL navigate to the Pet_Profile page for that Pet.
2. THE Pet_Profile page SHALL display the following information: pet name, species, breed, age, gender, size, color/markings, Health_Status (vaccination status, spayed/neutered status, known medical conditions), temperament description, compatibility notes (good with kids, other pets), location, and date listed.
3. THE Pet_Profile page SHALL display a photo gallery showing all uploaded photos for the Pet, with the ability to cycle through images.
4. WHEN a Pet has no additional photos beyond the primary photo, THE Pet_Profile page SHALL display only the primary photo without a gallery navigation control.
5. THE Pet_Profile page SHALL display an "Apply to Adopt" button for Pets with `Available` status when viewed by an authenticated Adopter.
6. WHEN an unauthenticated visitor views a Pet_Profile page, THE Portal SHALL display a prompt to log in or register before applying.
7. WHEN an Adopter has already submitted an Adoption_Application for a Pet, THE Pet_Profile page SHALL display the current Application_Status instead of the "Apply to Adopt" button.

---

### Requirement 6: Adoption Application Submission

**User Story:** As an Adopter, I want to submit an adoption application for a pet, so that I can formally request to adopt it.

#### Acceptance Criteria

1. WHEN an authenticated Adopter clicks "Apply to Adopt" on a Pet_Profile page, THE Portal SHALL display the adoption application form.
2. THE adoption application form SHALL collect: applicant's full name (pre-filled from account), contact phone number, home address, housing type (house/apartment/other), whether the applicant owns or rents, landlord contact (if renting), household members count, presence of other pets, previous pet ownership experience, reason for adoption, and agreement to a home visit.
3. WHEN an Adopter submits a complete and valid adoption application form, THE Portal SHALL create an Adoption_Application record with `Pending` status and display a submission confirmation message.
4. WHEN an Adopter submits an adoption application form with one or more required fields empty, THE Portal SHALL reject the submission and highlight the missing fields with error messages.
5. THE Portal SHALL prevent an Adopter from submitting more than one Adoption_Application per Pet.
6. WHEN an Adoption_Application is successfully submitted, THE Portal SHALL send a confirmation notification to the Adopter's registered email address.

---

### Requirement 7: Adoption Application Status Tracking

**User Story:** As an Adopter, I want to track the status of my adoption applications, so that I know where my request stands.

#### Acceptance Criteria

1. THE Portal SHALL provide an "My Applications" page accessible to authenticated Adopters.
2. THE "My Applications" page SHALL display all Adoption_Applications submitted by the logged-in Adopter, showing: pet name, pet photo, date submitted, and current Application_Status.
3. WHEN an Adopter clicks on an application entry, THE Portal SHALL display the full details of that Adoption_Application including the submitted form data.
4. WHEN an Admin updates the Application_Status of an Adoption_Application, THE Portal SHALL update the displayed status on the Adopter's "My Applications" page within the same session refresh.
5. WHEN an Adoption_Application status changes to `Approved` or `Rejected`, THE Portal SHALL send a notification to the Adopter's registered email address with the updated status and any Admin remarks.

---

### Requirement 8: Admin — Pet Management

**User Story:** As an Admin, I want to add, edit, and remove pet listings, so that the portal always reflects the current shelter inventory.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide a pet management section listing all Pets in the system regardless of adoption status.
2. WHEN an Admin submits the "Add Pet" form with all required fields (name, species, breed, age, gender, size, description, Health_Status, location, and at least one photo), THE Portal SHALL create a new Pet record with `Available` status.
3. WHEN an Admin submits the "Add Pet" form with one or more required fields missing, THE Portal SHALL reject the submission and display field-specific validation error messages.
4. WHEN an Admin edits an existing Pet record and saves changes, THE Portal SHALL update the Pet record and reflect the changes on the Pet_Profile page immediately.
5. WHEN an Admin uploads a photo for a Pet, THE Portal SHALL accept image files in JPEG, PNG, or WebP format with a maximum file size of 5 MB per image.
6. IF an Admin attempts to upload an image file exceeding 5 MB, THEN THE Portal SHALL reject the upload and display a file size error message.
7. WHEN an Admin marks a Pet as `Adopted`, THE Portal SHALL remove the Pet from the public browsing page and update all associated Adoption_Applications to reflect the outcome.
8. WHEN an Admin deletes a Pet record, THE Portal SHALL also delete all associated Adoption_Applications and uploaded photos for that Pet.

---

### Requirement 9: Admin — Adoption Application Management

**User Story:** As an Admin, I want to review, approve, and reject adoption applications, so that I can manage the adoption process efficiently.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide an applications management section displaying all Adoption_Applications across all Pets.
2. THE applications management section SHALL allow the Admin to filter applications by Application_Status, pet name, and submission date range.
3. WHEN an Admin views an Adoption_Application, THE Portal SHALL display the full application form data alongside the applicant's account information and the Pet_Profile summary.
4. WHEN an Admin sets an Adoption_Application status to `Under Review`, THE Portal SHALL update the Application_Status and record the timestamp of the status change.
5. WHEN an Admin approves an Adoption_Application, THE Portal SHALL set the Application_Status to `Approved`, set the associated Pet's status to `Adopted`, and automatically set all other `Pending` or `Under Review` applications for the same Pet to `Rejected`.
6. WHEN an Admin rejects an Adoption_Application, THE Portal SHALL set the Application_Status to `Rejected` and require the Admin to enter a rejection reason before saving.
7. THE Admin_Dashboard SHALL display a count of `Pending` applications as a badge on the applications management navigation item.

---

### Requirement 10: Admin — User Management

**User Story:** As an Admin, I want to view and manage Adopter accounts, so that I can maintain the integrity of the user base.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide a user management section listing all registered Adopter accounts with their name, email, registration date, and number of submitted applications.
2. WHEN an Admin deactivates an Adopter account, THE Portal SHALL prevent that Adopter from logging in and display an account deactivated message on login attempt.
3. WHEN an Admin reactivates a previously deactivated Adopter account, THE Authentication_System SHALL restore the Adopter's ability to log in.
4. THE Admin_Dashboard SHALL allow the Admin to view all Adoption_Applications submitted by a specific Adopter from within the user management section.
5. THE Portal SHALL prevent an Admin from deleting their own Admin account.

---

### Requirement 11: Pet Surrender Form

**User Story:** As a member of the public, I want to submit a surrender request for a pet I can no longer care for, so that the shelter can take the animal in.

#### Acceptance Criteria

1. THE Portal SHALL provide a publicly accessible pet surrender form that does not require user authentication.
2. THE surrender form SHALL collect: submitter's full name, contact phone number, contact email address, pet name, species, breed (optional), approximate age, gender, reason for surrender, current Health_Status description, and whether the pet is vaccinated.
3. WHEN a visitor submits a complete surrender form, THE Portal SHALL create a surrender request record and display a confirmation message with an estimated response timeframe of 2–3 business days.
4. WHEN a visitor submits a surrender form with required fields missing, THE Portal SHALL reject the submission and highlight the missing fields with error messages.
5. WHEN a surrender request is submitted, THE Portal SHALL send an email notification to the Admin's registered email address with the full surrender request details.
6. THE Admin_Dashboard SHALL display all submitted surrender requests in a dedicated section, showing submitter name, pet name, species, submission date, and a `New` or `Reviewed` status.
7. WHEN an Admin marks a surrender request as `Reviewed`, THE Portal SHALL update the status and allow the Admin to add internal notes.

---

### Requirement 12: Admin Dashboard Overview

**User Story:** As an Admin, I want a summary dashboard, so that I can quickly understand the current state of the portal at a glance.

#### Acceptance Criteria

1. THE Admin_Dashboard home page SHALL display summary statistics including: total number of Pets listed, number of Pets with `Available` status, number of `Pending` Adoption_Applications, total number of registered Adopters, and number of new surrender requests.
2. THE Admin_Dashboard SHALL display a recent activity feed showing the last 10 events (new applications, status changes, new registrations, new surrender requests) with timestamps.
3. WHEN an Admin clicks on a summary statistic card, THE Portal SHALL navigate to the corresponding management section filtered to the relevant data.

---

### Requirement 13: Responsive and Accessible UI

**User Story:** As any user, I want the portal to work well on any device and be accessible, so that I can use it comfortably regardless of my device or ability.

#### Acceptance Criteria

1. THE Portal SHALL render correctly and be fully functional on viewport widths from 320px (mobile) to 1920px (desktop).
2. THE Portal SHALL use semantic HTML elements (nav, main, section, article, header, footer) throughout all pages.
3. THE Portal SHALL provide descriptive alt text for all Pet images.
4. THE Portal SHALL ensure all interactive elements (buttons, links, form inputs) are keyboard-navigable and have visible focus indicators.
5. THE Portal SHALL maintain a color contrast ratio of at least 4.5:1 for all body text against its background, in compliance with WCAG 2.1 AA guidelines.
6. THE Portal SHALL display a consistent navigation bar on all pages showing the portal logo, primary navigation links, and the authenticated user's name with a logout option.

---

### Requirement 14: Data Persistence and Integrity

**User Story:** As an Admin, I want all portal data to be reliably stored and consistent, so that no information is lost or corrupted.

#### Acceptance Criteria

1. THE Portal SHALL store all Pet records, Adopter accounts, Adoption_Applications, and surrender requests in a relational database.
2. THE Portal SHALL enforce referential integrity so that an Adoption_Application cannot exist without a corresponding Pet record and Adopter account.
3. WHEN a database write operation fails, THE Portal SHALL log the error with a timestamp and return a user-facing error message without exposing internal error details.
4. THE Portal SHALL use parameterized queries or an ORM for all database interactions to prevent SQL injection.

---

### Requirement 15: Security

**User Story:** As a user, I want my data and the portal to be secure, so that my personal information is protected.

#### Acceptance Criteria

1. THE Authentication_System SHALL store passwords using bcrypt with a minimum cost factor of 10.
2. THE Portal SHALL enforce HTTPS for all pages and API endpoints in production.
3. THE Portal SHALL sanitize all user-supplied input before rendering it in HTML to prevent cross-site scripting (XSS) attacks.
4. THE Portal SHALL implement CSRF protection on all state-changing form submissions.
5. THE Portal SHALL rate-limit login attempts to a maximum of 5 failed attempts per IP address within a 15-minute window, after which THE Authentication_System SHALL temporarily block further login attempts from that IP for 15 minutes.
6. IF a rate limit block is triggered, THEN THE Authentication_System SHALL display a message informing the user to try again after 15 minutes.
