module pow_2_function(
    input wire [w-1 : 0] x,
    output wire [w-1 : 0] y
);
    wire x_sign = x[w-1];
    wire [frc_width-1 : 0] x_frc  = x[frc_width-1 : 0];
    wire [int_width-1 : 0] x_int  = x[w-2 : frc_width];

    wire [w-1 : 0] base    = {1'b1,x_frc};
    wire shift_needed = (x_int != {int_width{1'b0}}) && (x_int != {int_width{1'b1}});
    wire [w-1 : 0] y1, y2;

    assign y1 = x_sign ? (base >>> 1) : base ;
    assign y2 = x_sign ? (y1 >>> 1) : (y1 <<< 1);

    assign y = shift_needed ? y2 : y1;


endmodule