USE university_portal;

CREATE TABLE departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    building        VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE programs (
    program_id      INT AUTO_INCREMENT PRIMARY KEY,
    program_name    VARCHAR(100) NOT NULL,
    department_id   INT NOT NULL,
    degree_level    ENUM('Bachelor', 'Master', 'PhD') NOT NULL,
	duration_years  INT DEFAULT 0 CHECK (duration_years BETWEEN 0 AND 7),    
    
	FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE students (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    date_of_birth   DATE NOT NULL,
    enrollment_date DATE NOT NULL,
    program_id      INT NOT NULL,
    status          ENUM('Active','Graduated','Suspended','Withdrawn') NOT NULL DEFAULT 'Active',
    gpa             DECIMAL(3,2) DEFAULT 0.00 CHECK (gpa BETWEEN 0.00 AND 4.00),
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_student_status (status),
    INDEX idx_student_program (program_id)
) ENGINE=InnoDB;

CREATE TABLE user_accounts (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL UNIQUE,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('student','admin') NOT NULL DEFAULT 'student',
    last_login      DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE instructors (
    instructor_id   INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    department_id   INT NOT NULL,
    hire_date       DATE NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_instructor_department (department_id)
) ENGINE=InnoDB;

CREATE TABLE courses (
    course_id       INT AUTO_INCREMENT PRIMARY KEY,
    course_code     VARCHAR(10) NOT NULL UNIQUE,
    course_name     VARCHAR(150) NOT NULL,
    credits         TINYINT NOT NULL CHECK (credits BETWEEN 1 AND 6),
    department_id   INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE course_offerings (
    offering_id     INT AUTO_INCREMENT PRIMARY KEY,
    course_id       INT NOT NULL,
    instructor_id   INT NOT NULL,
    semester        ENUM('Fall','Spring','Summer') NOT NULL,
    academic_year   YEAR NOT NULL,
    capacity        INT NOT NULL CHECK (capacity > 0),
    room            VARCHAR(20),
    schedule        VARCHAR(50),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    UNIQUE KEY uq_offering (course_id, semester, academic_year, instructor_id),
    INDEX idx_offering_term (semester, academic_year)
) ENGINE=InnoDB;


CREATE TABLE enrollments (
    enrollment_id   INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    offering_id     INT NOT NULL,
    enrollment_date DATE NOT NULL,
    grade           VARCHAR(2),
    status          ENUM('Enrolled','Completed','Dropped') NOT NULL DEFAULT 'Enrolled',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE KEY uq_enrollment (student_id, offering_id),
    INDEX idx_enrollment_student (student_id),
    INDEX idx_enrollment_offering (offering_id)
) ENGINE=InnoDB;


CREATE TABLE tuition_payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    amount          DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_date    DATETIME NOT NULL,
    semester        ENUM('Fall','Spring','Summer') NOT NULL,
    academic_year   YEAR NOT NULL,
    payment_method  ENUM('Credit Card','Bank Transfer','Scholarship','Cash') NOT NULL,
    status          ENUM('Pending','Completed','Failed','Refunded') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_payment_student (student_id),
    INDEX idx_payment_status (status)
) ENGINE=InnoDB;

