`timescale 1ns / 1ps 

module tb_fhn;
    reg clk, rst;
    reg signed [15 : 0] i_stim;
    
    // Wires to hold the state (Output feeds back to Input)
    wire signed [15 : 0] v_out, w_out;

    localparam FRC_BITS = 12;
    real scaling_factor = 4096.0;

    // Instantiate Pipelined Core
    core uut(
        .clk(clk), 
        .rst(rst), 
        .i(i_stim),
        
        // --- THE FEEDBACK LOOP ---
        // We connect the Output Wire (v_out) to the Input Port (v)
        // This makes the neuron "remember" its state.
        .v(v_out),      // Input 'v' gets signal from 'v_out'
        .w_in(w_out),   // Input 'w_in' gets signal from 'w_out'
        
        // The core drives these outputs
        .v_out(v_out), 
        .w_out(w_out)
    );

    // Clock Generation
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

        // --- RESET SEQUENCE ---
        rst = 1; 
        i_stim = 0;
        #100;

        rst = 0;
        #100; 

        // --- STIMULUS 1: 0.5A ---
        i_stim = 16'd2048; 
        $display("Applying Stimulus (0.5)...");
        repeat (20000) begin // Increased length to see slow spikes
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        // --- STIMULUS 2: 0.0A ---
        i_stim = 16'd0;
        $display("Removing Stimulus...");
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        // --- STIMULUS 3: 1.0A ---
        i_stim = 16'd4096;
        $display("Applying Stimulus (1.0)...");
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end

        // --- STIMULUS 4: 0.5A ---
        i_stim = 16'd2048;
        $display("Applying half Stimulus...");
        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f,%d", $time, $signed(v_out), $signed(v_out)/scaling_factor, $signed(i_stim));
        end


        $display("Simulation Finished. Data written to data.csv");
        $fclose(file);
        $finish;
    end

endmodule