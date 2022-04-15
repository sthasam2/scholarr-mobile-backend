# Changelogs

## v.0.1.5: (Unstable) Additions, Modification and Fixes 

15 Apr, 2022

1. Add Classroom Content Logic (Not tested, unstable)
2. Add Classroom Logic
3. Add Schedules Logic
4. Add boilerplate plagiarism_detector, planner
5. Modify setting configs, some app logics, Migrations, etc.
6. Bug Fixes

## v.0.1.4: Add Class Group logics, Major Modifications, Additions, Refactoring, Fixes

17 Mar, 2022

1. Add Class Group views, serializers, etc.
2. Add decorator (@try_except_http_error_decorator) for try_except to catch errors
3. Refactor code to use @try_except_http_error_decorator for all api views
4. Modified Custom Base exception to use (status_code, message, verbose, cause) instead of (instance, message)
5. Added Permissions
6. Bug Fixes, Code Cleaning

## v.0.1.3: Replaced drf-yasg with drf-spectacular, Fixes

20 Feb, 2022

1. Relaplaced drf-yasg with drf-spectacular
2. Deployment Bug fixes

## v.0.1.2: Heroku Deployment configs

20 Feb, 2022

1. Configured Heroku deployment
2. Sorted and Beautified files
3. Bug fixes

## v.0.1.1: Database Modelling

17 Feb, 2022

1. Modelled database for Class-groups, Classroom, Class-contents, Schedules
2. Added documentations
3. Bug fixes

## v.0.1.0: Initial setup, Authentication, and Profile

6 Feb, 2022

1. Inital Django template setup
2. Authentication views: Register, Login, Logut, Password Reset, Email Verification, Account Activation, Deactivation, and Delete
3. Profile views: Detail, Setup Persona, Upload Pictures, Privacy
