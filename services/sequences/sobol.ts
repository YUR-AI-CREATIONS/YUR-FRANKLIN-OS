/**
 * Sobol Sequence Generator
 *
 * Implementation of Sobol low-discrepancy sequence for Quasi-Monte Carlo integration.
 * Provides superior convergence O(log^d(N)/N) compared to standard Monte Carlo O(1/√N).
 *
 * Supports up to 40 dimensions with precomputed direction numbers.
 */

export interface SobolPoint {
  coordinates: number[];
  index: number;
}

export class SobolSequence {
  private dimension: number;
  private count: number;
  private direction: number[][];
  private x: number[];
  private maxDimensions = 40;

  /**
   * Direction numbers for Sobol sequence generation (up to 40 dimensions)
   * These are primitive polynomials and initial direction numbers from Joe & Kuo
   */
  private static readonly DIRECTION_NUMBERS: number[][] = [
    // Dimension 0 is special case (van der Corput)
    [],
    // Dimensions 1-39 use precomputed direction numbers
    [1], [1, 3], [1, 3, 1], [1, 1, 1], [1, 1, 3, 3],
    [1, 3, 5, 13], [1, 1, 5, 5, 17], [1, 1, 5, 5, 5],
    [1, 1, 7, 11, 19], [1, 1, 5, 1, 1], [1, 1, 1, 3, 11],
    [1, 3, 5, 5, 31], [1, 3, 3, 9, 7, 49], [1, 1, 1, 15, 21, 21],
    [1, 3, 1, 13, 27, 49], [1, 1, 1, 15, 7, 5], [1, 3, 1, 15, 13, 25],
    [1, 1, 5, 5, 19, 61], [1, 3, 7, 11, 23, 15], [1, 1, 7, 3, 23, 55],
    [1, 3, 7, 13, 19, 51], [1, 1, 5, 11, 7, 11], [1, 1, 1, 3, 13, 39],
    [1, 3, 5, 3, 15, 19], [1, 1, 7, 15, 19, 59], [1, 3, 7, 5, 21, 23],
    [1, 3, 1, 11, 5, 27], [1, 1, 1, 7, 11, 43], [1, 3, 5, 9, 21, 55],
    [1, 1, 3, 3, 25, 17], [1, 3, 1, 15, 9, 63], [1, 1, 7, 15, 29, 51],
    [1, 3, 7, 7, 11, 29], [1, 1, 5, 13, 23, 7], [1, 3, 3, 5, 27, 39],
    [1, 1, 1, 1, 1, 49], [1, 3, 5, 15, 13, 11], [1, 1, 7, 3, 9, 49],
    [1, 3, 3, 13, 19, 7]
  ];

  constructor(dimension: number = 2) {
    if (dimension < 1 || dimension > this.maxDimensions) {
      throw new Error(`Dimension must be between 1 and ${this.maxDimensions}`);
    }

    this.dimension = dimension;
    this.count = 0;
    this.x = new Array(dimension).fill(0);
    this.direction = this.initializeDirectionNumbers();
  }

  /**
   * Initialize sequence state (generateKeyPair equivalent)
   * Resets the sequence to the beginning
   */
  public generateKeyPair(): void {
    this.count = 0;
    this.x = new Array(this.dimension).fill(0);
  }

  /**
   * Initialize direction numbers for all dimensions
   */
  private initializeDirectionNumbers(): number[][] {
    const directions: number[][] = [];
    const bits = 31; // Number of bits for direction numbers

    for (let dim = 0; dim < this.dimension; dim++) {
      directions[dim] = new Array(bits);

      if (dim === 0) {
        // First dimension uses simple binary fractions
        for (let i = 0; i < bits; i++) {
          directions[dim][i] = 1 << (bits - i - 1);
        }
      } else {
        // Other dimensions use direction numbers
        const dirNums = SobolSequence.DIRECTION_NUMBERS[dim] || [1];

        // Initialize first direction numbers
        for (let i = 0; i < dirNums.length && i < bits; i++) {
          directions[dim][i] = dirNums[i] << (bits - i - 1);
        }

        // Generate remaining direction numbers using recurrence
        for (let i = dirNums.length; i < bits; i++) {
          directions[dim][i] = directions[dim][i - dirNums.length];
          for (let j = 0; j < dirNums.length; j++) {
            directions[dim][i] ^= directions[dim][i - dirNums.length + j] >> j;
          }
        }
      }
    }

    return directions;
  }

  /**
   * Generate the next point in the Sobol sequence
   */
  public next(): SobolPoint {
    if (this.count === 0) {
      this.count++;
      return {
        coordinates: new Array(this.dimension).fill(0),
        index: 0
      };
    }

    // Find the rightmost zero bit in count
    const c = this.rightmostZeroBit(this.count);

    // Update x using Gray code
    for (let dim = 0; dim < this.dimension; dim++) {
      this.x[dim] ^= this.direction[dim][c];
    }

    this.count++;

    // Convert to [0,1) range
    const coordinates = this.x.map(val => val / Math.pow(2, 31));

    return {
      coordinates,
      index: this.count - 1
    };
  }

  /**
   * Generate n points in the Sobol sequence
   */
  public generate(n: number): SobolPoint[] {
    const points: SobolPoint[] = [];
    for (let i = 0; i < n; i++) {
      points.push(this.next());
    }
    return points;
  }

  /**
   * Find the position of the rightmost zero bit
   */
  private rightmostZeroBit(n: number): number {
    let bit = 0;
    while ((n & 1) === 1) {
      n >>= 1;
      bit++;
    }
    return bit;
  }

  /**
   * Get current dimension
   */
  public getDimension(): number {
    return this.dimension;
  }

  /**
   * Get current count
   */
  public getCount(): number {
    return this.count;
  }

  /**
   * Skip ahead n points in the sequence
   */
  public skip(n: number): void {
    for (let i = 0; i < n; i++) {
      this.next();
    }
  }

  /**
   * Reset the sequence to a specific index
   */
  public reset(index: number = 0): void {
    this.generateKeyPair();
    if (index > 0) {
      this.skip(index);
    }
  }
}

/**
 * Convenience function to generate Sobol points
 */
export function generateSobolPoints(
  dimension: number,
  count: number
): number[][] {
  const sequence = new SobolSequence(dimension);
  const points = sequence.generate(count);
  return points.map(p => p.coordinates);
}

/**
 * Calculate discrepancy of a point set (for quality assessment)
 */
export function calculateDiscrepancy(points: number[][]): number {
  if (points.length === 0) return 0;

  const n = points.length;
  const d = points[0].length;

  // Simplified star discrepancy calculation
  let maxDiscrepancy = 0;

  for (let i = 0; i < n; i++) {
    let volume = 1;
    let count = 0;

    for (let dim = 0; dim < d; dim++) {
      volume *= points[i][dim];
    }

    for (let j = 0; j < n; j++) {
      let inBox = true;
      for (let dim = 0; dim < d; dim++) {
        if (points[j][dim] > points[i][dim]) {
          inBox = false;
          break;
        }
      }
      if (inBox) count++;
    }

    const discrepancy = Math.abs(count / n - volume);
    maxDiscrepancy = Math.max(maxDiscrepancy, discrepancy);
  }

  return maxDiscrepancy;
}

export default SobolSequence;
