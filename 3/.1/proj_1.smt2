; [PART1-DECLARATIONS]

(declare-const x Int)
(declare-const y Int)
(declare-const a (Array Int Int))

; [PART2-PROGRAM]

; Assume x > 0 and y > 0
(assert (> x 0))
(assert (> y 0))

; Assign A[x] := y
(define-fun A1 () (Array Int Int) (store a x y))

; Conditional assignment based on x = y
(define-fun A2 () (Array Int Int) 
  (ite (= x y) 
    (store A1 y x) 
    (store A1 x y)))

; [PART3-CONJECTURE]

(define-fun F () Bool
    (and (= (* 2 (select A2 x)) (* 2 y)) 
         (> (* 2 (select A2 x)) 0)))

(assert (not F))
(check-sat)