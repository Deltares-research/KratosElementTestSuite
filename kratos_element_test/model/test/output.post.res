GiD Post Results File 1.2
GaussPoints "lin2_element_gp" ElemType Linear
Number Of Gauss Points: 2
  Nodes not included
Natural Coordinates: Internal
End GaussPoints
GaussPoints "tri3_element_gp" ElemType Triangle
Number Of Gauss Points: 3
Natural Coordinates: Given
0.166667 0.166667
0.666667 0.166667
0.166667 0.666667
End GaussPoints
Result "DISPLACEMENT" "Kratos" 0.2 Vector OnNodes
Values
1 0 0 0
2 -1.57277e-20 0 0
3 0 -3.73024e-20 0
4 -6.8956e-22 -1.39011e-20 0
5 0 0 0
6 -2.66985e-20 0 0
7 4.47703e-21 5.66383e-21 0
8 1.29019e-20 0 0
9 3.62327e-20 0 0
End Values
Result "WATER_PRESSURE" "Kratos" 0.2 Scalar OnNodes
Values
1 0
2 0
3 0
4 0
5 0
6 0
7 0
8 0
9 0
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.2 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.2 Matrix OnGaussPoints "tri3_element_gp"
Values
1 -100 -100 -100 1.84647e-14 0 0
 -100 -100 -100 2.2638e-15 0 0
 -100 -100 -100 -7.14568e-15 0 0
2 -100 -100 -100 -1.33796e-16 0 0
 -100 -100 -100 -1.32771e-14 0 0
 -100 -100 -100 -2.10509e-15 0 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.2 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.2 Scalar OnGaussPoints "tri3_element_gp"
Values
1 6.04e-14
 5.69785e-14
 4.43928e-14
2 2.31742e-16
 2.70332e-14
 4.27882e-14
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.2 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.2 Scalar OnGaussPoints "tri3_element_gp"
Values
1 -100
 -100
 -100
2 -100
 -100
 -100
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.2 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.2 Matrix OnGaussPoints "tri3_element_gp"
Values
1 -1.39164e-20 6.53373e-20 -1.73927e-20 2.66712e-20 0 0
 1.32666e-20 -8.38721e-20 9.79028e-21 3.26993e-21 0 0
 3.41242e-20 -3.70696e-20 2.02191e-20 -1.03215e-20 0 0
2 2.26771e-20 2.05951e-20 1.31448e-20 -1.93261e-22 0 0
 -9.59766e-21 -2.06027e-21 -1.80429e-20 -1.9178e-20 0 0
 -1.91115e-20 3.70696e-20 -2.35754e-20 -3.04069e-21 0 0
End Values
Result "DISPLACEMENT" "Kratos" 0.4 Vector OnNodes
Values
1 0 -0.05 0
2 0.0075 -0.05 0
3 0 -0.025 0
4 0.0075 -0.025 0
5 0 0 0
6 0.015 -0.05 0
7 0.015 -0.025 0
8 0.0075 0 0
9 0.015 0 0
End Values
Result "WATER_PRESSURE" "Kratos" 0.4 Scalar OnNodes
Values
1 0
2 0
3 0
4 0
5 0
6 0
7 0
8 0
9 0
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.4 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.4 Matrix OnGaussPoints "tri3_element_gp"
Values
1 -100 -45100 -100 4.80385e-12 0 0
 -100 -45100 -100 3.60289e-12 0 0
 -100 -45100 -100 -6.00481e-12 0 0
2 -100 -45100 -100 4.80385e-12 0 0
 -100 -45100 -100 1.20096e-12 0 0
 -100 -45100 -100 -4.80385e-12 0 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.4 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.4 Scalar OnGaussPoints "tri3_element_gp"
Values
1 45000
 45000
 45000
2 45000
 45000
 45000
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.4 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.4 Scalar OnGaussPoints "tri3_element_gp"
Values
1 -15100
 -15100
 -15100
2 -15100
 -15100
 -15100
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.4 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.4 Matrix OnGaussPoints "tri3_element_gp"
Values
1 0.015 -0.05 0.015 6.93889e-18 0 0
 0.015 -0.05 0.015 5.20417e-18 0 0
 0.015 -0.05 0.015 -8.67362e-18 0 0
2 0.015 -0.05 0.015 6.93889e-18 0 0
 0.015 -0.05 0.015 1.73472e-18 0 0
 0.015 -0.05 0.015 -6.93889e-18 0 0
End Values
Result "DISPLACEMENT" "Kratos" 0.6 Vector OnNodes
Values
1 0 -0.1 0
2 0.015 -0.1 0
3 0 -0.05 0
4 0.015 -0.05 0
5 0 0 0
6 0.03 -0.1 0
7 0.03 -0.05 0
8 0.015 0 0
9 0.03 0 0
End Values
Result "WATER_PRESSURE" "Kratos" 0.6 Scalar OnNodes
Values
1 0
2 0
3 0
4 0
5 0
6 0
7 0
8 0
9 0
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.6 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.6 Matrix OnGaussPoints "tri3_element_gp"
Values
1 -100 -90100 -100 9.6077e-12 0 0
 -100 -90100 -100 7.20577e-12 0 0
 -100 -90100 -100 -4.80385e-12 0 0
2 -100 -90100 -100 9.6077e-12 0 0
 -100 -90100 -100 2.40192e-12 0 0
 -100 -90100 -100 -1.44115e-11 0 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.6 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.6 Scalar OnGaussPoints "tri3_element_gp"
Values
1 90000
 90000
 90000
2 90000
 90000
 90000
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.6 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.6 Scalar OnGaussPoints "tri3_element_gp"
Values
1 -30100
 -30100
 -30100
2 -30100
 -30100
 -30100
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.6 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.6 Matrix OnGaussPoints "tri3_element_gp"
Values
1 0.03 -0.1 0.03 1.38778e-17 0 0
 0.03 -0.1 0.03 1.04083e-17 0 0
 0.03 -0.1 0.03 -6.93889e-18 0 0
2 0.03 -0.1 0.03 1.38778e-17 0 0
 0.03 -0.1 0.03 3.46945e-18 0 0
 0.03 -0.1 0.03 -2.08167e-17 0 0
End Values
Result "DISPLACEMENT" "Kratos" 0.8 Vector OnNodes
Values
1 0 -0.15 0
2 0.0225 -0.15 0
3 0 -0.075 0
4 0.0225 -0.075 0
5 0 0 0
6 0.045 -0.15 0
7 0.045 -0.075 0
8 0.0225 0 0
9 0.045 0 0
End Values
Result "WATER_PRESSURE" "Kratos" 0.8 Scalar OnNodes
Values
1 0
2 0
3 0
4 0
5 0
6 0
7 0
8 0
9 0
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.8 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 0.8 Matrix OnGaussPoints "tri3_element_gp"
Values
1 -100 -135100 -100 4.80385e-11 0 0
 -100 -135100 -100 1.92154e-11 0 0
 -100 -135100 -100 -4.80385e-12 0 0
2 -100 -135100 -100 1.92154e-11 0 0
 -100 -135100 -100 3.1225e-11 0 0
 -100 -135100 -100 -2.16173e-11 0 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.8 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "VON_MISES_STRESS" "Kratos" 0.8 Scalar OnGaussPoints "tri3_element_gp"
Values
1 135000
 135000
 135000
2 135000
 135000
 135000
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.8 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 0.8 Scalar OnGaussPoints "tri3_element_gp"
Values
1 -45100
 -45100
 -45100
2 -45100
 -45100
 -45100
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.8 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 0.8 Matrix OnGaussPoints "tri3_element_gp"
Values
1 0.045 -0.15 0.045 6.93889e-17 0 0
 0.045 -0.15 0.045 2.77556e-17 0 0
 0.045 -0.15 0.045 -6.93889e-18 0 0
2 0.045 -0.15 0.045 2.77556e-17 0 0
 0.045 -0.15 0.045 4.51028e-17 0 0
 0.045 -0.15 0.045 -3.1225e-17 0 0
End Values
Result "DISPLACEMENT" "Kratos" 1 Vector OnNodes
Values
1 0 -0.2 0
2 0.03 -0.2 0
3 0 -0.1 0
4 0.03 -0.1 0
5 0 0 0
6 0.06 -0.2 0
7 0.06 -0.1 0
8 0.03 0 0
9 0.06 0 0
End Values
Result "WATER_PRESSURE" "Kratos" 1 Scalar OnNodes
Values
1 0
2 0
3 0
4 0
5 0
6 0
7 0
8 0
9 0
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 1 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "CAUCHY_STRESS_TENSOR" "Kratos" 1 Matrix OnGaussPoints "tri3_element_gp"
Values
1 -100 -180100 -100 5.76462e-11 0 0
 -100 -180100 -100 2.40192e-11 0 0
 -100 -180100 -100 -4.80385e-12 0 0
2 -100 -180100 -100 0 0 0
 -100 -180100 -100 -4.80385e-12 0 0
 -100 -180100 -100 -4.80385e-12 0 0
End Values
Result "VON_MISES_STRESS" "Kratos" 1 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "VON_MISES_STRESS" "Kratos" 1 Scalar OnGaussPoints "tri3_element_gp"
Values
1 180000
 180000
 180000
2 180000
 180000
 180000
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 1 Scalar OnGaussPoints "lin2_element_gp"
Values
1 0
 0
End Values
Result "MEAN_EFFECTIVE_STRESS" "Kratos" 1 Scalar OnGaussPoints "tri3_element_gp"
Values
1 -60100
 -60100
 -60100
2 -60100
 -60100
 -60100
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 1 Matrix OnGaussPoints "lin2_element_gp"
Values
End Values
Result "ENGINEERING_STRAIN_TENSOR" "Kratos" 1 Matrix OnGaussPoints "tri3_element_gp"
Values
1 0.06 -0.2 0.06 8.32667e-17 0 0
 0.06 -0.2 0.06 3.46945e-17 0 0
 0.06 -0.2 0.06 -6.93889e-18 0 0
2 0.06 -0.2 0.06 0 0 0
 0.06 -0.2 0.06 -6.93889e-18 0 0
 0.06 -0.2 0.06 -6.93889e-18 0 0
End Values
