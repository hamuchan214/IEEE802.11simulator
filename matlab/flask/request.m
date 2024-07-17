% Define the base URL of the Flask API
baseUrl = 'http://127.0.0.1:5000/';

% Define the option value to be sent (0 for default, 1 for 'hello matlab')
optionValue = 1; % Change this to 0 or 1 as needed

% Create the full URL with the query parameter
url = sprintf('%s?option=%d', baseUrl, optionValue);

% Send an HTTP GET request to the Flask API
response = webread(url);

% Display the response from the Flask API
disp(response);
