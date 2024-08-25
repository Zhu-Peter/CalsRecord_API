CREATE TABLE `users` (
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
)

-- contains session keys for login
create table session (
    id int not null,
    token varchar(255) not null,
    foreign key (id) references users(id) on delete cascade
);

-- stores session keys for login and returns the session key
DELIMITER $$
$$
CREATE DEFINER=`root`@`localhost` PROCEDURE calsrecord.set_token(input_id int, input_token varchar(255))
begin
	insert into calsrecord.session (id, token) values (input_id, input_token);
	commit;
    select * from session where token = input_token;
END$$
DELIMITER ;

-- USERS
-- GET
create procedure get_user(user_id int)
    select * from users where id = user_id;

-- POST
DELIMITER $$
$$
create DEFINER=`root`@`localhost` procedure `create_user`(
    email_input varchar(255),
    first_name_input varchar(255),
    last_name_input varchar(255),
    password_input varchar(255)
)
begin
    insert into user (email, first_name, last_name, password) values
        (email_input, first_name_input, last_name_input, password_input);
    commit;
    select id from user where id = last_insert_id();
end$$
DELIMITER ;

-- PATCH
DELIMITER $$
$$
create DEFINER=`root`@`localhost` procedure `update_user`(
    email_input varchar(255),
    first_name_input varchar(255),
    last_name_input varchar(255),
    password_input varchar(255),
    token_input varchar(255)
)
begin
    DECLARE token_id int;
    select user_id into token_id from user_session where token = token_input;

    IF token_id IS NULL THEN

        ROLLBACK;

        SELECT 'Invalid token' AS message;

    ELSE
        IF email_input IS NOT NULL THEN
            update user set email = email_input where id = token_id;
        END IF;
        IF first_name_input IS NOT NULL THEN
            update user set first_name = first_name_input where id = token_id;
        END IF;
        IF last_name_input IS NOT NULL THEN
            update user set last_name = last_name_input where id = token_id;
        END IF;
        IF password_input IS NOT NULL THEN
            update user set password = password_input where id = token_id;
        END IF;
        COMMIT;
        select 'Success' AS message;
        
    END IF;
end$$
DELIMITER ;

-- DELETE
DELIMITER $$
$$
create DEFINER=`root`@`localhost` procedure `delete_user`(password_input varchar(255), token_input varchar(255))
begin
    DECLARE token_id int;
    DECLARE check_pwd varchar(255);
    select user_id into token_id from user_session where token = token_input;

    IF token_id IS NULL THEN

        ROLLBACK;

        SELECT 'Invalid token' AS message;

    ELSE
        SELECT password INTO check_pwd FROM user WHERE id = token_id;

        IF check_pwd!= password_input THEN
            ROLLBACK;
            SELECT 'Invalid password' AS message;
        ELSE
            DELETE FROM user WHERE id = token_id;
            COMMIT;
            SELECT 'Success' AS message;
        END IF;
    END IF;
end$$
DELIMITER ;

-- LOGIN
create procedure user_login(email_input varchar(255), password_input varchar(255))
    select id from user where email = email_input and password = password_input;

-- LOGOUT
DELIMITER $$
$$
create DEFINER=`root`@`localhost` procedure ` user_logout`(token_input varchar(255))
begin
    delete from session where token = token_input;
    commit;
    SELECT 'Success' AS message;
end$$
DELIMITER ;