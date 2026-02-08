import SobolSequence from '../sequences/sobol';

interface IntegrationResult {
  value: number;
  error: number;
  variance: number;
  samples: number;
  method: string;
}

export class QMCIntegrator {
  private sobol: SobolSequence;

  constructor(dimension: number) {
    this.sobol = new SobolSequence(dimension);
  }

  async integrate(
    f: (x: number[]) => number,
    samples: number = 10000
  ): Promise<IntegrationResult> {
    console.log('🎲 Starting QMC integration...');

    let sum = 0;
    let sumSquared = 0;
    const points = this.sobol.generate(samples);

    for (const point of points) {
      const value = f(point.coordinates);
      sum += value;
      sumSquared += value * value;
    }

    const mean = sum / samples;
    const variance = (sumSquared / samples) - (mean * mean);
    const error = Math.sqrt(variance / samples);

    console.log(`✅ QMC complete: ${mean} ± ${error}`);

    return { value: mean, error, variance, samples, method: 'sobol' };
  }

  async compareWithMC(f: (x: number[]) => number, samples: number) {
    console.log('📊 Comparing QMC vs Monte Carlo...');
    const qmcResult = await this.integrate(f, samples);
    const mcResult = await this.monteCarloIntegrate(f, samples);

    const improvement = mcResult.error / qmcResult.error;
    console.log(`📈 QMC is ${improvement.toFixed(2)}x more accurate`);

    return { qmc: qmcResult, mc: mcResult, improvement };
  }

  private async monteCarloIntegrate(
    f: (x: number[]) => number,
    samples: number
  ): Promise<IntegrationResult> {
    let sum = 0;
    let sumSquared = 0;
    const dimension = this.sobol.getDimension();

    for (let i = 0; i < samples; i++) {
      const point = Array.from({ length: dimension }, () => Math.random());
      const value = f(point);
      sum += value;
      sumSquared += value * value;
    }

    const mean = sum / samples;
    const variance = (sumSquared / samples) - (mean * mean);

    return {
      value: mean,
      error: Math.sqrt(variance / samples),
      variance,
      samples,
      method: 'monte-carlo'
    };
  }
}

export default QMCIntegrator;
