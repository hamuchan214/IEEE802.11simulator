classdef User
    properties
        id
        n = 0
        slots = 0
        transmitted = 0
        CW
        total_data_transmitted = 0
    end

    methods
        function obj = User(id)
            obj.id = id;
            obj.CW = obj.calculate_CW();
        end

        function CW = calculate_CW(obj)
            slot_time = 9 * 10^(-6);
            cw_max = 2^(4 + obj.n) - 1;
            slots = randi([1, min(cw_max, 1023)]);
            obj.slots = slots;
            CW = slots * slot_time;
        end

        function obj = re_transmit(obj)
            obj.n = obj.n + 1;
            obj.CW = obj.calculate_CW();
        end

        function obj = reset_CW(obj)
            obj.n = 0;
            obj.CW = obj.calculate_CW();
        end
    end
end
