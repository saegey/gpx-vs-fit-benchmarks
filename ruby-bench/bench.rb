#!/usr/bin/env ruby
# Benchmark FIT parsing with ridewithgps/rubyfit
# Usage: ruby bench.rb <fit_file> [iters]

require "json"
require "rubyfit"

fit_path = ARGV[0] || "../testdata/BWR_San_Diego_Waffle_Ride_.fit"
iters = (ARGV[1] || 25).to_i
raw = File.binread(fit_path)

class NullCallbacks
  def initialize
    @record_count = 0
  end
  attr_reader :record_count

  # Swallow all callbacks; increment on names containing "record" when possible
  def method_missing(name, *args)
    if name.to_s.downcase.include?("record")
      @record_count += 1
    end
  end

  def respond_to_missing?(_name, _priv = false)
    true
  end
end

# warm-up parse
cb = NullCallbacks.new
RubyFit::FitParser.new(cb).parse(raw)

# run benchmark
samples = []
iters.times do
  cb = NullCallbacks.new
  t0 = Process.clock_gettime(Process::CLOCK_MONOTONIC)
  RubyFit::FitParser.new(cb).parse(raw)
  dt = (Process.clock_gettime(Process::CLOCK_MONOTONIC) - t0) * 1000.0
  samples << dt
end

samples.sort!
mean = samples.sum / samples.length
p50 = samples[samples.length / 2]
p95 = samples[(samples.length * 0.95).floor - 1]
min = samples.first
max = samples.last

result = {
  label: "FIT (rubyfit)",
  n: iters,
  bytes: raw.bytesize,
  mean_ms: mean,
  p50_ms: p50,
  p95_ms: p95,
  min_ms: min,
  max_ms: max,
}

puts "FIT (rubyfit): mean=#{format('%.2f', mean)}ms p50=#{format('%.2f', p50)}ms p95=#{format('%.2f', p95)}ms min=#{format('%.2f', min)}ms max=#{format('%.2f', max)}ms n=#{iters}"
# Also emit JSON if requested via env
if ENV["JSON"] == "1"
  puts JSON.pretty_generate(result)
end
