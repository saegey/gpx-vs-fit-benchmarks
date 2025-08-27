# ruby_bench/handler.rb
# Point Bundler at the vendored bundle (relative to this file)
ENV["BUNDLE_GEMFILE"] = File.expand_path(File.join(__dir__, "Gemfile"))
ENV["BUNDLE_PATH"]    = File.expand_path(File.join(__dir__, "vendor", "bundle"))
require "bundler/setup"    # <-- sets $LOAD_PATH for all gems

require "json"
require "time"
require_relative "bench"

WARM = { value: false } # simple warm-flag in module scope

def handle(event:, context:)
  t_start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
  puts "[rb] start ts=#{(Time.now.to_f*1000).to_i} cold=#{!WARM[:value]}"
  # Inputs
  iters   = (event && event["iterations"]) || 25
  fit_rel = "testdata/BWR_San_Diego_Waffle_Ride_.fit"
  fit_path = File.expand_path(File.join(__dir__, fit_rel))

  # Run benchmark
  t0 = Process.clock_gettime(Process::CLOCK_MONOTONIC)
  result = RubyFitBench.run(fit_path: fit_path, iters: iters)
  puts format('[rb] bench done in %.2fms', (Process.clock_gettime(Process::CLOCK_MONOTONIC)-t0)*1000.0)

  # Emit a plain JSON result line (good for Logs Insights)
  now_ms = (Time.now.to_f * 1000).to_i
  out = {
    ts: now_ms,
    lang: "Ruby",
    format: result[:format],
    parser: result[:parser],
    iterations: result[:iterations],
    mean_ms: result[:mean_ms],
    p50_ms: result[:p50_ms],
    p95_ms: result[:p95_ms],
    min_ms: result[:min_ms],
    max_ms: result[:max_ms],
    memory_mb: (ENV["AWS_LAMBDA_FUNCTION_MEMORY_SIZE"] || "0").to_i,
    cold: !WARM[:value],
    commit: ENV["COMMIT_SHA"] || "dev"
  }
  puts JSON.generate(out)

  # (Optional) Also emit EMF metrics so you can graph them without parsing logs
  # emf = {
  #   "_aws" => {
  #     "Timestamp" => now_ms,
  #     "CloudWatchMetrics" => [{
  #       "Namespace" => "GPXvsFIT/Benchmarks",
  #       "Dimensions" => [["Language","Format","Parser","MemoryMB","Cold"]],
  #       "Metrics" => [
  #         {"Name"=>"mean_ms","Unit"=>"Milliseconds"},
  #         {"Name"=>"p50_ms","Unit"=>"Milliseconds"},
  #         {"Name"=>"p95_ms","Unit"=>"Milliseconds"},
  #       ]
  #     }]
  #   },
  #   "Language"=>"Ruby",
  #   "Format"=>result[:format],
  #   "Parser"=>result[:parser],
  #   "MemoryMB"=>(ENV["AWS_LAMBDA_FUNCTION_MEMORY_SIZE"] || "0").to_i,
  #   "Cold"=>!WARM[:value],
  #   "mean_ms"=>result[:mean_ms],
  #   "p50_ms"=>result[:p50_ms],
  #   "p95_ms"=>result[:p95_ms]
  # }
  # puts JSON.generate(emf)

  WARM[:value] = true
  puts format('[rb] total handler time %.2fms', (Process.clock_gettime(Process::CLOCK_MONOTONIC)-t_start)*1000.0)
  { ok: true, count: 1 }
end