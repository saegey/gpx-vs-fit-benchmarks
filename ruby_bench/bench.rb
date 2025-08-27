# ruby_bench/bench.rb

# Do NOT define VENDOR here; handler already added vendor paths to $LOAD_PATH.
# Also no Bundler here — simpler and avoids init warnings.

require "json"
require "rubyfit"

module RubyFitBench
  module_function

  class NullCallbacks
    def initialize; @record_count = 0; end
    attr_reader :record_count
    def method_missing(name, *args)
      @record_count += 1 if name.to_s.downcase.include?("record")
    end
    def respond_to_missing?(_name, _priv = false) = true
  end

  def run_once(raw)
    cb = NullCallbacks.new
    t0 = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    RubyFit::FitParser.new(cb).parse(raw)
    (Process.clock_gettime(Process::CLOCK_MONOTONIC) - t0) * 1000.0
  end

  def summarize(samples, n, bytes)
    s = samples.sort
    mean = s.sum / s.length
    p50  = s[s.length / 2]
    p95i = [(s.length * 0.95).floor - 1, 0].max
    {
      format: "FIT",
      parser: "rubyfit",
      iterations: n,
      bytes: bytes,
      mean_ms: mean,
      p50_ms: p50,
      p95_ms: s[p95i],
      min_ms: s.first,
      max_ms: s.last
    }
  end

  # main bench entry
  def run(fit_path:, iters: 25)
    raw = File.binread(fit_path)
    # warm-up
    RubyFit::FitParser.new(NullCallbacks.new).parse(raw)

    samples = Array.new(iters) { run_once(raw) }
    summarize(samples, iters, raw.bytesize)
  end
end