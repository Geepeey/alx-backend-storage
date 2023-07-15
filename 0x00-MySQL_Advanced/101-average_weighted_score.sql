-- Write a SQL script that creates a stored procedure ComputeAverageWeighted
-- ScoreForUsers that computes and store the average weighted score for all students

DELIMITER //

CREATE PROCEDURE ComputeAverageWeightedScoreForUsers()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE user_id INT;
    DECLARE total_score FLOAT;
    DECLARE total_weight FLOAT;
    DECLARE weighted_average FLOAT;
    
    -- Cursor to iterate through users
    DECLARE cur_users CURSOR FOR SELECT id FROM users;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur_users;
    
    read_loop: LOOP
        FETCH cur_users INTO user_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        SET total_score = 0;
        SET total_weight = 0;
        
        -- Calculate total score and total weight for the current user
        SELECT SUM(c.score * p.weight) INTO total_score
        FROM corrections c
        JOIN projects p ON c.project_id = p.id
        WHERE c.user_id = user_id;
        
        SELECT SUM(p.weight) INTO total_weight
        FROM corrections c
        JOIN projects p ON c.project_id = p.id
        WHERE c.user_id = user_id;
        
        IF total_weight IS NOT NULL AND total_weight <> 0 THEN
            SET weighted_average = total_score / total_weight;
        ELSE
            SET weighted_average = 0;
        END IF;
        
        -- Update average_score for the current user
        UPDATE users
        SET average_score = weighted_average
        WHERE id = user_id;
    END LOOP;
    
    CLOSE cur_users;
    
END //

DELIMITER ;

