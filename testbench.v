`timescale 1ns / 1ps 

module tb_fhn;
    reg clk, rst;
    reg signed [15 : 0] i_stim;
    wire signed [15 : 0] v_out, w_out;

    localparam FRC_BITS = 12;
    real scaling_factor = 4096.0;

    core uut(
        .clk(clk), 
        .rst(rst), 
        .i(i_stim),
        .v(v_out),
        .w_in(w_out),
        .v_out(v_out), 
        .w_out(w_out)
    );

    initial clk = 0;
    always #5 clk = ~clk;
    
    integer file;

    initial begin 
        $dumpfile("fhn_sim.vcd");
        $dumpvars(0, tb_fhn);

        file = $fopen("data.csv", "w");
        if (file == 0) begin
            $display("Error: Could not open file.");
            $finish;
        end
        
        $fdisplay(file, "time_step,v_raw,v_float,i_raw");

        rst = 1; 
        i_stim = 0;
        #100;
        rst = 0;
        #100; 

        i_stim = 16'd2048; 
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        i_stim = 16'd0;
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        i_stim = 16'd4096;
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        i_stim = 16'd2048;
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        $fclose(file);
        $finish;
    end
endmodule
