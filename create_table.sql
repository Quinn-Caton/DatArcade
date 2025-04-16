CREATE TABLE Games (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255),
    rating FLOAT,
    rating_count INT,
    release_date DATE,
    genres NVARCHAR(MAX),
    platforms NVARCHAR(MAX),
    companies NVARCHAR(MAX)
);