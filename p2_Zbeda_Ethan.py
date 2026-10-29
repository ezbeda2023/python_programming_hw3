from __future__ import annotations


class ParkingPermit:

    def __init__(
        self, owner: str, months: int, fee_schedule: dict[str, float]
    ) -> None:
        if not isinstance(owner, str):
            raise TypeError("Owner must be a string")
        if not owner.strip():
            raise ValueError("Owner must not be empty")
        if not isinstance(months, int) or isinstance(months, bool):
            raise TypeError("Months must be an integer")
        if months <= 0:
            raise ValueError("Months must be positive")
        if not isinstance(fee_schedule, dict):
            raise TypeError("Fee schedule must be a dictionary")
        for fee in fee_schedule.values():
            if not isinstance(fee, (int, float)) or isinstance(fee, bool):
                raise TypeError("Fees must be numbers")
            if not 0 <= fee < float("inf"):
                raise ValueError("Fees must be finite and nonnegative")
        fee_schedule["monthly_rate"]
        self.owner = owner
        self.months = months
        self.fee_schedule = dict(fee_schedule)

    def cost(self) -> float:
        return float(self.months * self.fee_schedule["monthly_rate"])

    def __str__(self) -> str:
        return (
            f"{self.owner} | {type(self).__name__} | "
            f"{self.months} month(s) | Cost: ${self.cost():.2f}"
        )

    def __repr__(self) -> str:
        return (
            f"ParkingPermit(owner={self.owner!r}, months={self.months!r}, "
            f"fee_schedule={self.fee_schedule!r})"
        )


class StudentPermit(ParkingPermit):

    def __init__(
        self,
        owner: str,
        months: int,
        fee_schedule: dict[str, float],
        vehicles: int,
    ) -> None:
        super().__init__(owner, months, fee_schedule)
        if not isinstance(vehicles, int) or isinstance(vehicles, bool):
            raise TypeError("Vehicles must be an integer")
        if vehicles < 1:
            raise ValueError("At least one vehicle must be registered")
        self.fee_schedule["additional_vehicle_fee"]
        self.vehicles = vehicles

    def cost(self) -> float:
        return float(
            super().cost()
            + (self.vehicles - 1) * self.fee_schedule["additional_vehicle_fee"]
        )

    def __str__(self) -> str:
        return f"{super().__str__()} | Vehicles: {self.vehicles}"

    def __repr__(self) -> str:
        return (
            f"StudentPermit(owner={self.owner!r}, months={self.months!r}, "
            f"fee_schedule={self.fee_schedule!r}, vehicles={self.vehicles!r})"
        )


class FacultyPermit(ParkingPermit):

    def __init__(
        self,
        owner: str,
        months: int,
        fee_schedule: dict[str, float],
        garage_access: bool,
    ) -> None:
        super().__init__(owner, months, fee_schedule)
        if not isinstance(garage_access, bool):
            raise TypeError("Garage access must be a Boolean")
        self.fee_schedule["garage_monthly_rate"]
        self.garage_access = garage_access

    def cost(self) -> float:
        garage_fee = (
            self.months * self.fee_schedule["garage_monthly_rate"]
            if self.garage_access
            else 0.0
        )
        return float(super().cost() + garage_fee)

    def __str__(self) -> str:
        return f"{super().__str__()} | Garage access: {self.garage_access}"

    def __repr__(self) -> str:
        return (
            f"FacultyPermit(owner={self.owner!r}, months={self.months!r}, "
            f"fee_schedule={self.fee_schedule!r}, "
            f"garage_access={self.garage_access!r})"
        )


def summarize_list(permits: list[ParkingPermit]) -> float:
    total = 0.0
    for permit in permits:
        print(str(permit))
        total += permit.cost()
    return total


def main() -> None:
    student_fees = {"monthly_rate": 25.0, "additional_vehicle_fee": 10.0}
    faculty_fees = {"monthly_rate": 40.0, "garage_monthly_rate": 15.0}
    permits: list[ParkingPermit] = [
        StudentPermit("Ethan Zbeda", 4, student_fees, vehicles=1),
        StudentPermit("Alex Rivera", 4, student_fees, vehicles=3),
        FacultyPermit("Dr. Morgan Lee", 4, faculty_fees, garage_access=False),
        FacultyPermit("Dr. Taylor Chen", 4, faculty_fees, garage_access=True),
    ]

    print("Ethan Zbeda | FAU student ID: ezbeda2023")
    print("\nPermit objects (__repr__):")
    for permit in permits:
        print(repr(permit))

    print("\nPermit summary (__str__):")
    total = summarize_list(permits)
    print(f"\nTotal revenue: ${total:.2f}")


if __name__ == "__main__":
    main()
