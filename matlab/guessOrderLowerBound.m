function n = guessOrderLowerBound(d,t)
    if rem(t,2) == 0
        e = t/2;
        n = nchoosek(d + e - 1, d - 1) + nchoosek(d + e - 2, d - 1);
    elseif rem(t,2) == 1
        e = (t-1)/2;
        n = 2*nchoosek(d + e - 1, d - 1);
    end
end