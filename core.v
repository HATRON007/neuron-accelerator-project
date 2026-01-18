module core #(    //#() called module's parameter port list
    // Constants
    localparam tau_shift = 1,
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

    wire signed [w-1 : 0] pow2_pos, pow2_neg;
    wire signed [19 : 0] z1, z2, z5;
    wire signed [19 : 0] v_ext, w_ext, i_ext, diff_ext;
    wire signed [w-1 : 0] z3, z4, z6, z7;

    assign v_ext = {{4{v[w-1]}}, v};
    assign w_ext = {{4{w_out[w-1]}}, w_out};
    assign i_ext = {{4{i[w-1]}}, i};
    

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

    assign diff_ext = {{4{pow2_neg[w-1]}} , pow2_neg} - {{4{pow2_pos[w-1]}}, pow2_pos};
    assign z1 = (diff_ext <<< 1) + diff_ext;
    assign z2 = (v_ext <<< 2) + v_ext;
    assign z3 = v + a - (w_out >>> 1);

    assign z4 = (z3 + 128) >>> total_shift;
    //assign z4 = (z3) >>> total_shift;
    assign z5 = z1 + z2 - w_ext + i_ext;
    assign z6 = w_out + z4;
    assign z7 = v + $signed((z5 + 64) >>> time_shift);
    //assign z7 = v + $signed((z5) >>> time_shift);
    // Combinational Logic
    // assign z1 = ((pow2_neg - pow2_pos) <<< 1) + (pow2_neg - pow2_pos);  // 3 * (2^-v - 2^v)
    // assign z2 = (v <<< 2) + v;                                          // 5 * v
    // assign z3 = v + a - (w_out >>> 1);                                  // v + a - 0.5w
    // assign z4 = z3 >>> total_shift;                                     // (dt/tau) * z3
    // assign z5 = z1 + z2 - w_out + i;                                    // 5v + g(v) - w + I
    
    // assign z6 = w_out + z4;             // Next W
    // assign z7 = (z5 >>> time_shift) + v; // Next V (Fixed: used time_shift)
    
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