INSERT INTO book
(title, author, total_Pages, current_Page, status_id)
VALUES
(
    'English Grammar in Use',
    'Raymond Murphy',
    320,
    1,
    (SELECT id FROM constant
     WHERE name = 'reading' AND type = 'BookState')
),
(
    'English Vocabulary in Use',
    'Michael McCarthy',
    260,
    1,
    (SELECT id FROM constant
     WHERE name = 'reading' AND type = 'BookState')
),
(
    'Atomic Habits',
    'James Clear',
    320,
    1,
    (SELECT id FROM constant
     WHERE name = 'planned' AND type = 'BookState')
);

go

INSERT INTO studySchedule
(title, description, start_Date, end_Date, status_id)
VALUES
(
    'English Daily Reading',
    'Daily English reading plan',
    '2026-08-13',
    '2026-09-30',
    (SELECT id FROM constant
     WHERE name = 'active' AND type = 'StudyScheduleStatus')
);

go

INSERT INTO studyScheduleItem
(
    Schedule_id,
    book_id,
    Weekday_id,
    pages
)
VALUES

-- Thursday
(
    1,
    1,
    (SELECT id
     FROM constant
     WHERE name = 'thursday'
       AND type = 'Weekday'),
    3
),

(
    1,
    2,
    (SELECT id
     FROM constant
     WHERE name = 'thursday'
       AND type = 'Weekday'),
    4
),

-- Friday
(
    1,
    1,
    (SELECT id
     FROM constant
     WHERE name = 'friday'
       AND type = 'Weekday'),
    6
),

(
    1,
    2,
    (SELECT id
     FROM constant
     WHERE name = 'friday'
       AND type = 'Weekday'),
    7
),

-- Saturday
(
    1,
    1,
    (SELECT id
     FROM constant
     WHERE name = 'saturday'
       AND type = 'Weekday'),
    9
);