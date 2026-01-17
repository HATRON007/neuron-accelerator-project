module core #(
    // Constants
    localparam tau_shift = 2,
    localparam time_shift = 7,
    localparam total_shift = tau_shift + time_shift,

    // Widths
    parameter int_width = 3,
    parameter frc_width = 12,
    localparam w = 1 + int_width + frc_width, // Total Width
    
    // Coefficient 'a'
    localparam signed [w-1 : 0] a = 16'd2867
)(
    input  wire clk,
    input  wire rst,
    input  wire signed [w-1 : 0] i,
    output reg  signed [w-1 : 0] v,
    output reg  signed [w-1 : 0] w_out
);

    wire signed [w-1 : 0] pow2_pos, pow2_neg, z1, z2, z3, z4, z5, z6, z7;

    // Instantiation
    pow_2_function #(
        .w(w), 
        .int_width(int_width), 
        .frc_width(frc_width)
    ) positive_v (.x(v), .y(pow2_pos));
    pow_2_function #(
        .w(w), 
        .int_width(int_width), 
        .frc_width(frc_width)
    ) negative_v (.x(-v), .y(pow2_neg));

    // Combinational Logic
    assign z1 = ((pow2_neg - pow2_pos) <<< 1) + (pow2_neg - pow2_pos);  // 3 * (2^-v - 2^v)
    assign z2 = (v <<< 2) + v;                                          // 5 * v
    assign z3 = v + a - (w_out >>> 1);                                  // v + a - 0.5w
    assign z4 = z3 >>> total_shift;                                     // (dt/tau) * z3
    assign z5 = z1 + z2 - w_out + i;                                    // 5v + g(v) - w + I
    
    assign z6 = w_out + z4;             // Next W
    assign z7 = (z5 >>> time_shift) + v; // Next V (Fixed: used time_shift)
    
    // Sequential Logic
    always @(posedge clk or posedge rst) begin
      if (rst) begin
        v <= 16'hECE1;
        w_out <= 16'hF600;
      end
      else begin
        v <= z7;
        w_out <= z6;
      end 
    end
    
endmodule