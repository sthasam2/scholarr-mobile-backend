# POSTGRES SETUP

* [Linux](docs/database_setup.md#linux-system)
* [Windows](docs/database_setup.md#windows-system)

---

## Linux System

 **OS:** UBUNTU 20.10


Source: [Digital Ocean Setup Postgres]([https://link](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-16-04))

### Steps for Linux

Follow the given steps to setup postgresql with django on your ubuntu machine

### Install components from ubuntu repositories

The following components are required for setting up postgresql with django

**Pre-Requirements**: python3, pip3, libpq

``` BASH
sudo apt install python3-pip python3-dev libpq-dev
```

**PostgreSQl componenets**: postgresql, postgresql-contrib

``` BASH
sudo apt install postgresql postgresql-contrib
```

### Create a Database and User

We need to setup a database ourselves. repeat the given steps to do so

* #### **Database**

1. Open postgres session

``` BASH
sudo -u postgres psql
```

2. Create database

``` SQL
CREATE DATABASE <name_of_database>;
```

*Note: Angular brackets <> denotes custom naming. DO NOT USE ANGULAR BRACKETS*

* #### **User**

``` SQL
CREATE USER <user_name> WITH PASSWORD 'password'; 
```

**Give permission to the user**

``` SQL
GRANT ALL PRIVILEGES ON DATABASE <db> TO <user>;
```

**Now we need to perform some additional steps to customize postgres according to Django preferences.**

``` SQL
ALTER ROLE user_name SET client_encoding TO 'utf8';
ALTER ROLE user_name SET default_transaction_isolation TO 'read committed';
ALTER ROLE user_name SET timezone TO 'UTC';
```

With this your database is setup on your linux machine

## Check created database

1. open postgres

``` BASH
sudo -u postgres psql
```

or 

``` BASH
bash$: sudo -i -u postgres
postgres$: psql
```

2. List Databases on the postgres server

 `\l`

**Output**:

``` 

                                  List of databases
   Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges   
-----------+----------+----------+-------------+-------------+-----------------------
 apps | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =Tc/postgres         +
           |          |          |             |             | postgres=CTc/postgres+
           |          |          |             |             | admin=CTc/postgres
 postgres  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | 
 template0 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
(4 rows)
```

---

## Windows System

 **OS:** WINDOWS 10

Source: [PostgreSQL on Windows]([https://link](https://www.postgresqltutorial.com/install-postgresql/))

## Steps for Windows

There are three steps to complete the PostgreSQL installation:

1. Download PostgreSQL installer for Windows
2. Install PostgreSQL
3. Verify the installation

### 1. Download PostgreSQL Installer for Windows

First, you need to go to the download page of [PostgreSQL installers on the EnterpriseDB](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).

Second, click the download link as shown below:

![Download PostgreSQL](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Download-PostgreSQL.png)

It will take a few minutes to complete the download.

### 2. Install PostgreSQL on Window step by step

To install PostgreSQL on Windows, you need to have administrator
privileges.

Step 1. Double click on the installer file, an installation wizard will
appear and guide you through multiple steps where you can choose
different options that you would like to have in PostgreSQL.

Step 2. Click the Next button

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-1.png)

Step 3. Specify installation folder, choose your own or keep the default
folder suggested by PostgreSQL installer and click the Next button

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-2.png)

Step 4. Select software components to install:

* The PostgreSQL Server to install the PostgreSQL database server
* pgAdmin 4 to install the PostgreSQL database GUI management tool.
* Command Line Tools to install command-line tools such as psql, 

    pg\_restore, etc. These tools allow you to interact with the
    PostgreSQL database server using the command-line interface.

* Stack Builder provides a GUI that allows you to download and install

    drivers that work with PostgreSQL.

For the tutorial on this website, you don’t need to install Stack
Builder so feel free to uncheck it and click the Next button to select
the data directory:

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-3.png)

Step 5. Select the database directory to store the data or accept the
default folder. And click the Next button to go to the next step:

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-4.png)

Step 6. Enter the password for the database superuser (postgres)

PostgreSQL runs as a service in the background under a service account
named `postgres` . If you already created a service account with the name
`postgres` , you need to provide the password of that account in the
following window.

After entering the password, you need to retype it to confirm and click
the Next button:

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-5.png)

Step 7. Enter a port number on which the PostgreSQL database server will
listen. The default port of PostgreSQL is 5432. You need to make sure
that no other applications are using this port.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-6.png)

Step 8. Choose the default locale used by the PostgreSQL database. If
you leave it as default locale, PostgreSQL will use the operating system
locale. After that click the Next button.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-7.png)

Step 9. The setup wizard will show the summary information of
PostgreSQL. You need to review it and click the Next button if
everything is correct. Otherwise, you need to click the Back button to
change the configuration accordingly.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-8.png)

Now, you’re ready to install PostgreSQL on your computer. Click the
**Next** button to begin installing PostgreSQL.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-9.png)

The installation may take a few minutes to complete.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-10.png)

Step 10. Click the **Finish** button to complete the PostgreSQL
installation.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-12-Windows-Step-11.png)

### 3.  **Verify the Installation**

There are several ways to verify the PostgreSQL installation. You can
try to [connect to the
PostgreSQL](https://www.postgresqltutorial.com/connect-to-postgresql-database/ "Connect to PostgreSQL Database")
database server from any client application e.g., * *psql and pgAdmin.

The quick way to verify the installation is through the psql program.

First, click the `psql` application to launch it. The psql command-line
program will display.

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-psql.png)

Second, enter all the necessary information such as the server, 
database, port, username, and password. To accept the default, you can
press **Enter**.  Note that you should provide the password that you
entered during installing the PostgreSQL.

``` {.wp-block-code aria-describedby="shcb-language-1" data-shcb-language-name="Shell Session" data-shcb-language-slug="shell"}
Server [localhost]:
Database [postgres]:
Port [5432]:
Username [postgres]:
Password for user postgres:
psql (12.3)
WARNING: Console code page (437) differs from Windows code page (1252)

         8-bit characters might not work correctly. See psql reference
         page "Notes for Windows users" for details.

Type "help" for help.

postgres=#Code language: Shell Session (shell)
```

Third, issue the command `SELECT version();` you will see the following
output:

![alt](https://www.postgresqltutorial.com/wp-content/uploads/2020/07/Install-PostgreSQL-psql-verification.png)

Congratulation! you’ve successfully installed PostgreSQL database server on your local system.
