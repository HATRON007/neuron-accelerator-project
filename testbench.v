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
        
        // CSV Header: Consistent 4 columns
        $fdisplay(file, "time_step,v_raw,v_float,i_raw");

        rst = 1; 
        i_stim = 0;
        #100;

        rst = 0;
        #100; 

        // --- STIMULUS PHASE ---
        i_stim = 16'd2048; 
        $display("Applying Stimulus...");
        repeat (4000) begin
            @(posedge clk);
            // write 4 columns
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        // --- RELAXATION PHASE ---
        i_stim = 16'd0;
        $display("Removing Stimulus...");
        repeat (20000) begin
            @(posedge clk);
            // FIXED: write 4 columns here too (i_stim is 0)
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        i_stim = 16'd4096;
        $display("Applying Stimulus...");
        repeat (10000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        i_stim = 16'd2048;
        $display("Applying half Stimulus...");
        repeat (4000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        i_stim = 16'd1024;
        $display("Applying half Stimulus...");
        repeat (4000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end


        $display("Simulation Finished. Data written to data.csv");
        $fclose(file);
        $finish;
    end

endmodule