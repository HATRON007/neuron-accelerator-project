`timescale 1ns / 1ps 

module tb_fhn;
    reg clk, rst;
    reg signed [15 : 0] i_stim;
    wire signed [15 : 0] v_out, w_out;

    core uut(
        .clk(clk), .rst(rst), .i(i_stim),
        .v(v_out), .w_out(w_out)
    );

    initial clk = 0;
    always #5 clk = ~clk;
    initial begin 
        $dumpfile("fhn_sim.vcd");
        $dumpvars(0, tb_fhn);
        rst = 1; i_stim = 0;
        #100
        rst = 0;

        #500             //let neuron sits at rest
        i_stim = 16'd3277;
        #100000

        $finish;
    end

endmodule