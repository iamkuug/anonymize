DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    address VARCHAR(255)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    shipping_address VARCHAR(255),
    order_date DATE
);

INSERT INTO users (email, phone, password, address)
VALUES 
('user1@example.com', '1234567890', 'password1', '123 Main St.'),
('user2@example.com', '0987654321', 'password2', '456 Elm St.'),
('user3@example.com', '5551112222', 'password3', '789 Oak Lane'),
('user4@example.com', '7778889999', 'password4', '321 Pine Road'),
('user5@example.com', '4445556666', 'password5', '654 Maple Avenue'),
('user6@example.com', '2223334444', 'password6', '987 Cedar Street'),
('user7@example.com', '6667778888', 'password7', '258 Birch Boulevard'),
('user8@example.com', '3334445555', 'password8', '159 Spruce Court'),
('user9@example.com', '9876543210', 'password9', '741 Willow Way'),
('user10@example.com', '1112223333', 'password10', '852 Redwood Drive'),
('user13@example.com', '2228889999', 'password13', '487 Aspen Court'),
('user14@example.com', '6543211234', 'password14', '619 Elm Grove'),
('user15@example.com', '9998887777', 'password15', '753 Maple Ridge'),
('user16@example.com', '4447770000', 'password16', '246 Pine Valley'),
('user17@example.com', '1239874560', 'password17', '582 Oak Terrace'),
('user18@example.com', '7410852963', 'password18', '914 Cedar Hills'),
('user19@example.com', '3698521470', 'password19', '357 Birch Street'),
('user20@example.com', '9630258741', 'password20', '681 Willow Creek'),
('user21@example.com', '4561237890', 'password21', '132 Spruce Lane'),
('user22@example.com', '7890123456', 'password22', '465 Maple Court'),
('user23@example.com', '2343214321', 'password23', '798 Pine Street'),
('user24@example.com', '8765432109', 'password24', '231 Oak Boulevard'),
('user25@example.com', '5432167890', 'password25', '564 Cedar Road'),
('user26@example.com', '3210987654', 'password26', '897 Elm Avenue'),
('user27@example.com', '6543210987', 'password27', '321 Birch Way'),
('user28@example.com', '9876543210', 'password28', '654 Redwood Lane'),
('user29@example.com', '1234567890', 'password29', '987 Sycamore Drive'),
('user30@example.com', '7890123456', 'password30', '258 Juniper Street'),
('user31@example.com', '4561237890', 'password31', '591 Aspen Road'),
('user32@example.com', '2109876543', 'password32', '824 Maple Grove'),
('user33@example.com', '6789054321', 'password33', '147 Pine Court'),
('user34@example.com', '3456789012', 'password34', '480 Oak Lane'),
('user35@example.com', '8901234567', 'password35', '713 Cedar Street'),
('user36@example.com', '5678901234', 'password36', '246 Elm Boulevard'),
('user37@example.com', '9012345678', 'password37', '579 Birch Avenue'),
('user38@example.com', '2345678901', 'password38', '912 Willow Road'),
('user39@example.com', '6789012345', 'password39', '345 Spruce Way'),
('user40@example.com', '4567890123', 'password40', '678 Maple Lane'),
('user41@example.com', '7890123456', 'password41', '201 Pine Avenue'),
('user42@example.com', '3456789012', 'password42', '534 Oak Court'),
('user43@example.com', '8901234567', 'password43', '867 Cedar Drive'),
('user44@example.com', '5678901234', 'password44', '190 Elm Lane'),
('user45@example.com', '9012345678', 'password45', '423 Birch Road'),
('user46@example.com', '2345678901', 'password46', '756 Willow Street'),
('user47@example.com', '6789012345', 'password47', '289 Spruce Boulevard'),
('user48@example.com', '4567890123', 'password48', '612 Maple Court'),
('user49@example.com', '7890123456', 'password49', '945 Pine Lane'),
('user50@example.com', '3456789012', 'password50', '278 Oak Avenue'),
('user51@example.com', '8901234567', 'password51', '611 Cedar Way'),
('user52@example.com', '5678901234', 'password52', '944 Elm Drive'),
('user53@example.com', '9012345678', 'password53', '277 Birch Street'),
('user54@example.com', '2345678901', 'password54', '610 Willow Court'),
('user55@example.com', '6789012345', 'password55', '943 Spruce Road'),
('user56@example.com', '4567890123', 'password56', '276 Maple Boulevard'),
('user57@example.com', '7890123456', 'password57', '609 Pine Lane'),
('user58@example.com', '3456789012', 'password58', '942 Oak Street'),
('user59@example.com', '8901234567', 'password59', '275 Cedar Avenue'),
('user60@example.com', '5678901234', 'password60', '608 Elm Way'),
('user61@example.com', '9012345678', 'password61', '941 Birch Drive'),
('user62@example.com', '2345678901', 'password62', '274 Willow Lane'),
('user63@example.com', '6789012345', 'password63', '607 Spruce Court'),
('user64@example.com', '4567890123', 'password64', '940 Maple Road'),
('user65@example.com', '7890123456', 'password65', '273 Pine Boulevard'),
('user66@example.com', '3456789012', 'password66', '606 Oak Street'),
('user67@example.com', '8901234567', 'password67', '939 Cedar Lane'),
('user68@example.com', '5678901234', 'password68', '272 Elm Avenue'),
('user69@example.com', '9012345678', 'password69', '605 Birch Way'),
('user70@example.com', '2345678901', 'password70', '938 Willow Drive'),
('user71@example.com', '6789012345', 'password71', '271 Spruce Street'),
('user72@example.com', '4567890123', 'password72', '604 Maple Court'),
('user73@example.com', '7890123456', 'password73', '937 Pine Lane'),
('user74@example.com', '3456789012', 'password74', '270 Oak Boulevard'),
('user75@example.com', '8901234567', 'password75', '603 Cedar Road'),
('user76@example.com', '5678901234', 'password76', '936 Elm Street'),
('user77@example.com', '9012345678', 'password77', '269 Birch Avenue'),
('user78@example.com', '2345678901', 'password78', '602 Willow Way'),
('user79@example.com', '6789012345', 'password79', '935 Spruce Drive'),
('user80@example.com', '4567890123', 'password80', '268 Maple Lane'),
('user81@example.com', '7890123456', 'password81', '601 Pine Court'),
('user82@example.com', '3456789012', 'password82', '934 Oak Street'),
('user83@example.com', '8901234567', 'password83', '267 Cedar Avenue'),
('user84@example.com', '5678901234', 'password84', '600 Elm Boulevard'),
('user85@example.com', '9012345678', 'password85', '933 Birch Road'),
('user86@example.com', '2345678901', 'password86', '266 Willow Lane'),
('user87@example.com', '6789012345', 'password87', '599 Spruce Street'),
('user88@example.com', '4567890123', 'password88', '932 Maple Way'),
('user89@example.com', '7890123456', 'password89', '265 Pine Drive'),
('user90@example.com', '3456789012', 'password90', '598 Oak Court'),
('user91@example.com', '8901234567', 'password91', '931 Cedar Lane'),
('user92@example.com', '5678901234', 'password92', '264 Elm Avenue'),
('user93@example.com', '9012345678', 'password93', '597 Birch Street'),
('user94@example.com', '2345678901', 'password94', '930 Willow Boulevard'),
('user95@example.com', '6789012345', 'password95', '263 Spruce Road'),
('user96@example.com', '4567890123', 'password96', '596 Maple Court'),
('user97@example.com', '7890123456', 'password97', '929 Pine Lane'),
('user98@example.com', '3456789012', 'password98', '262 Oak Way'),
('user99@example.com', '8901234567', 'password99', '595 Cedar Drive'),
('user100@example.com', '5678901234', 'password100', '928 Elm Street');

INSERT INTO orders (shipping_address, order_date)
VALUES 
('123 Main St.', '2023-01-01'),
('456 Elm St.', '2023-01-02'),
('789 Oak Lane', '2023-02-15'),
('321 Pine Road', '2023-02-20'),
('654 Maple Avenue', '2023-03-05'),
('987 Cedar Street', '2023-03-10'),
('258 Birch Boulevard', '2023-04-01'),
('159 Spruce Court', '2023-04-12'),
('741 Willow Way', '2023-05-01'),
('852 Redwood Drive', '2023-05-15'),
('123 Main St.', '2023-06-01'),
('456 Elm St.', '2023-06-10'),
('789 Oak Lane', '2023-07-01'),
('321 Pine Road', '2023-07-15'),
('654 Maple Avenue', '2023-08-01'),
('987 Cedar Street', '2023-08-20'),
('258 Birch Boulevard', '2023-09-01'),
('159 Spruce Court', '2023-09-15'),
('741 Willow Way', '2023-10-01'),
('852 Redwood Drive', '2023-10-20'),
('123 Main St.', '2025-03-30'),
('456 Elm St.', '2025-04-01'),
('789 Oak Lane', '2025-04-15'),
('321 Pine Road', '2025-04-30'),
('654 Maple Avenue', '2025-05-01'),
('987 Cedar Street', '2025-05-15'),
('258 Birch Boulevard', '2025-05-30'),
('159 Spruce Court', '2025-06-01'),
('741 Willow Way', '2025-06-15'),
('852 Redwood Drive', '2025-06-30'),
('123 Main St.', '2025-07-01'),
('456 Elm St.', '2025-07-15'),
('789 Oak Lane', '2025-07-30'),
('321 Pine Road', '2025-08-01'),
('654 Maple Avenue', '2025-08-15'),
('987 Cedar Street', '2025-08-30'),
('258 Birch Boulevard', '2025-09-01'),
('159 Spruce Court', '2025-09-15'),
('741 Willow Way', '2025-09-30'),
('852 Redwood Drive', '2025-10-01'),
('123 Main St.', '2025-10-15'),
('456 Elm St.', '2025-10-30'),
('789 Oak Lane', '2025-11-01'),
('321 Pine Road', '2025-11-15'),
('654 Maple Avenue', '2025-11-30'),
('987 Cedar Street', '2025-12-01'),
('258 Birch Boulevard', '2025-12-15'),
('159 Spruce Court', '2025-12-30'),
('741 Willow Way', '2026-01-01'),
('852 Redwood Drive', '2026-01-15');