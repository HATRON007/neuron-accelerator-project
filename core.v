module core #(
    localparam tau_shift = 2,
    localparam time_shift = 7,
    localparam total_shift = tau_shift + time_shift,

    parameter int_width = 3,
    parameter frc_width = 12,
    localparam w = 1 + int_width + frc_width

)(
    input wire clk,
    input wire rst,
    input wire signed [w-1 : 0] i,
    output reg signed [w-1 : 0] v
);

    
