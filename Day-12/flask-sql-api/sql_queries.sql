CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    course VARCHAR(100),
    marks INT
);

INSERT INTO students (name, age, course, marks) VALUES ('Alice', 20, 'CS', 85);
INSERT INTO students (name, age, course, marks) VALUES ('Bob', 22, 'Math', 75);

SELECT * FROM students;
SELECT name FROM students;
SELECT * FROM students WHERE marks > 80;
SELECT * FROM students ORDER BY marks DESC;
SELECT COUNT(*) FROM students;
SELECT AVG(marks) FROM students;
SELECT MAX(marks) FROM students;
SELECT MIN(marks) FROM students;
SELECT course, COUNT(*) FROM students GROUP BY course;
SELECT * FROM students WHERE age BETWEEN 18 AND 25;
SELECT DISTINCT course FROM students;
UPDATE students SET marks = 95 WHERE id = 1;
DELETE FROM students WHERE id = 2;
SELECT * FROM students LIMIT 5;
SELECT * FROM students WHERE name LIKE 'A%';
SELECT * FROM students WHERE marks IN (70, 80, 90);
SELECT course, AVG(marks) FROM students GROUP BY course;
SELECT * FROM students ORDER BY age ASC;
SELECT * FROM students WHERE marks IS NOT NULL;