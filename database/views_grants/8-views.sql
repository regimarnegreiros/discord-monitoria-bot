CREATE VIEW semester_data AS
SELECT sem.semester AS "semester", sem.semester_year AS "year",
    sub.subject_name as "subject", (ss.question_data).total as "total questions",
    (ss.question_data).answered as "answered questions",
    (ss.question_data).solved as "solved questions"
FROM semester_subject ss
    JOIN semester sem ON sem.semesterID = ss.semesterID
    JOIN subjects sub ON sub.subjectID = ss.subjectID;
