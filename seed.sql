CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  role VARCHAR(20) NOT NULL,
  team_id INTEGER
);

CREATE TABLE IF NOT EXISTS timesheets (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  date DATE NOT NULL,
  hours FLOAT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  team_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS holidays (
  id INTEGER PRIMARY KEY,
  date DATE NOT NULL,
  name VARCHAR(100) NOT NULL
);

INSERT INTO users (id, name, role, team_id) VALUES
(1, 'Komal', 'employee', 1),
(2, 'Aarav', 'employee', 1),
(3, 'Meera', 'teamlead', 1),
(4, 'Rohan', 'manager', 1),
(5, 'Anita', 'hr', NULL),
(6, 'Vikram', 'admin', NULL);

INSERT INTO timesheets (id, user_id, date, hours) VALUES
(1, 1, '2026-01-09', 8.0),
(2, 1, '2026-01-10', 7.5),
(3, 2, '2026-01-10', 8.0),
(4, 3, '2026-01-10', 9.0),
(5, 4, '2026-01-10', 8.5);

INSERT INTO projects (id, name, team_id) VALUES
(1, 'Payroll Revamp', 1),
(2, 'Attendance Analytics', 1);

INSERT INTO holidays (id, date, name) VALUES
(1, '2026-01-26', 'Republic Day'),
(2, '2026-03-08', 'Holi'),
(3, '2026-08-15', 'Independence Day');

INSERT INTO users (id, name, role, team_id) VALUES
  (7, 'Sneha', 'employee', 2),
  (8, 'Rahul', 'employee', 2),
  (9, 'Priya', 'teamlead', 2),
  (10, 'Manish', 'manager', 2),
  (11, 'Deepa', 'employee', 3),
  (12, 'Sahil', 'teamlead', 3);

INSERT INTO timesheets (id, user_id, date, hours) VALUES
  (6, 7, '2026-01-05', 8.0),
  (7, 7, '2026-01-06', 7.5),
  (8, 8, '2026-01-06', 8.0),
  (9, 9, '2026-01-07', 8.5),
  (10, 10, '2026-01-07', 9.0),
  (11, 11, '2026-01-08', 6.0),
  (12, 12, '2026-01-08', 8.0),
  (13, 1, '2026-01-05', 8.0),
  (14, 2, '2026-01-05', 7.0),
  (15, 3, '2026-01-06', 8.5),
  (16, 4, '2026-01-06', 8.0),
  (17, 1, '2026-01-07', 8.0),
  (18, 2, '2026-01-07', 7.5),
  (19, 8, '2026-01-08', 8.0),
  (20, 9, '2026-01-09', 9.0);

INSERT INTO projects (id, name, team_id) VALUES
  (3, 'Recruitment Portal', 2),
  (4, 'Onboarding Automation', 2),
  (5, 'Benefits Dashboard', 3);

INSERT INTO holidays (id, date, name) VALUES
  (4, '2026-04-02', 'Good Friday'),
  (5, '2026-11-04', 'Diwali'),
  (6, '2026-12-25', 'Christmas Day');