function simulate_transmission(duration)
    rng(123);
    users = User.empty(5,0);
    for i = 1:5
        users(i) = User(i);
    end
    
    current_time = 0;
    collision_count = 0;
    data_transmission = 1500; % 1500bit
    transmission_rate = 12 * 10^6; % 12Mbps

    while current_time < duration
        cw_times = zeros(5, 2);
        for i = 1:5
            cw_times(i, :) = [users(i).id, users(i).CW];
        end
        cw_times = sortrows(cw_times, 2);

        min_user_id = cw_times(1, 1);
        min_cw = cw_times(1, 2);
        min_user = users(min_user_id);

        collisions = [];
        for i = 1:5
            if users(i).CW == min_cw && users(i).id ~= min_user_id
                collisions = [collisions, users(i)];
            end
        end

        if ~isempty(collisions)
            disp([collisions.id]);
            for i = 1:5
                fprintf('User %d CW = %.6f seconds (waited %d slots)\n', users(i).id, users(i).CW, users(i).slots);
            end

            trans_time = transmission_time(data_transmission, transmission_rate);
            if current_time + min_cw + trans_time <= duration
                current_time = current_time + min_cw;
                current_time = current_time + trans_time;
                collision_count = collision_count + 1;
            else
                current_time = duration;
                collision_count = collision_count + 1;
            end

            fprintf('\nTime: %fs - Collision detected! Users: [%s]\n', current_time, sprintf('%d ', [collisions.id, min_user_id]));

            for user = [collisions, min_user]
                fprintf('User %d waited %d slots before collision.\n', user.id, user.slots);
                user = user.re_transmit();
            end
            fprintf('\n');
        else
            trans_time = transmission_time(data_transmission, transmission_rate);
            if current_time + trans_time <= duration
                current_time = current_time + min_cw;
                min_user.transmitted = min_user.transmitted + 1;
                min_user.total_data_transmitted = min_user.total_data_transmitted + data_transmission;
                current_time = current_time + trans_time;
            else
                remaining_time = duration - current_time;
                current_time = duration;
                data_transmitted = remaining_time * transmission_rate;
                min_user.total_data_transmitted = min_user.total_data_transmitted + data_transmitted;
                min_user.transmitted = min_user.transmitted + 1;
            end

            for i = 1:5
                if users(i).id ~= min_user_id
                    users(i).CW = users(i).CW - min_user.CW;
                    users(i).slots = users(i).slots - min_user.slots;
                end
            end

            min_user = min_user.reset_CW();
        end
    end

    fprintf('\nSimulation ended. Results:\n');
    for i = 1:5
        user = users(i);
        average_transmission_rate = user.total_data_transmitted / duration / 10^6;
        fprintf('User %d transmitted %d times, total data transmitted: %d bits, average transmission rate: %.2f Mbps\n', user.id, user.transmitted, user.total_data_transmitted, average_transmission_rate);
    end
    fprintf('Total collisions: %d\n', collision_count);
end

function time = transmission_time(data, rate)
    time = data / rate;
end
