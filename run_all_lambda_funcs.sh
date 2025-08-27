set -e
STAGE=${1:-dev}
FUNCS=(nodeFit nodeGpx pyFit pyGpx goFit goGpx rubyFit)
for fn in "${FUNCS[@]}"; do
	echo -e "\n--- $fn ---"
	npx serverless invoke -f "$fn" --stage "$STAGE" -l || echo "$fn failed"
done