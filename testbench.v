`timescale 1ns / 1ps

module tb_tdm;

    parameter NEURON_COUNT = 500;
    parameter DATA_WIDTH = 16;
    
    reg clk;
    reg rst;
    reg signed [DATA_WIDTH-1:0] i_stim;
    // reg [$clog2(NEURON_COUNT)-1:0] monitor_id;
    
    // wire signed [DATA_WIDTH-1:0] v_mon;
    // wire signed [DATA_WIDTH-1:0] w_mon;

    tdm_controller #(
        .neuron_count(NEURON_COUNT),
        .pipeline_depth(5),
        .data_width(DATA_WIDTH)
    ) uut (
        .clk(clk),
        .rst(rst),
        .i_stim(i_stim)
        // .monitor_id(monitor_id),
        // .v_out_monitor(v_mon),
        // .w_out_monitor(w_mon)
    );

    integer file;
    real v_real;

    initial clk = 0;
    always #5 clk = ~clk; 

    initial begin
        file = $fopen("data.csv", "w");
        $fdisplay(file, "time_ns,neuron_id,v_float,i_raw");
        
        // monitor_id = 0;
        i_stim = 0;
        rst = 1;
        #100;
        
        rst = 0;
        #100;
        
        i_stim = 16'd4096; 
        
        repeat(NEURON_COUNT * 4000) begin
            @(posedge clk);
        end
        
        i_stim = 0;
        
        repeat(NEURON_COUNT * 4000) begin
            @(posedge clk);
        end

        i_stim = 16'd2048; 
        
        repeat(NEURON_COUNT * 4000) begin
            @(posedge clk);
        end

        $fclose(file);
        $finish;
    end

    always @(posedge clk) begin
        if (!rst) begin
            v_real = $signed(uut.core_v_out) / 4096.0;
            $fdisplay(file, "%0d,%0d,%0f,%0d", $time, uut.ptr_write, v_real, $signed(i_stim));
        end
    end

endmodule