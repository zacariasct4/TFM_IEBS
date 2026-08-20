import json
import numpy as np
import tensorflow as tf
import pandas as pd

from time import perf_counter
from sklearn.model_selection import ParameterSampler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
)

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping

class MacroF1Callback(tf.keras.callbacks.Callback):

    def __init__(
        self,
        X_val,
        y_val,
        n_classes,
    ):
        super().__init__()

        self.X_val = X_val
        self.y_val = y_val
        self.n_classes = n_classes

    def on_epoch_end(self, epoch, logs=None):

        logs = logs or {}

        y_prob = self.model.predict(
            self.X_val,
            verbose=0,
        )

        if self.n_classes == 2:
            y_pred = (
                y_prob.ravel() >= 0.5
            ).astype(int)

        else:
            y_pred = np.argmax(
                y_prob,
                axis=1,
            )

        macro_f1 = f1_score(
            self.y_val,
            y_pred,
            average="macro",
        )

        logs["val_macro_f1"] = macro_f1

        print(
            f" - val_macro_f1: {macro_f1:.4f}",
            end="",
        )

def get_class_weights(y):
    classes = np.unique(y)

    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y,
    )

    return {
        int(cls): float(weight)
        for cls, weight in zip(classes, weights)
    }


def build_baseline_mlp(
    input_dim,
    n_classes,
    random_state=42,
):
    tf.keras.backend.clear_session()
    tf.random.set_seed(random_state)

    model = tf.keras.Sequential([
        tf.keras.layers.Input(
            shape=(input_dim,)
        ),
        tf.keras.layers.Dense(
            64,
            activation="relu",
        ),
        tf.keras.layers.Dense(
            32,
            activation="relu",
        ),
    ])

    if n_classes == 2:
        model.add(
            tf.keras.layers.Dense(
                1,
                activation="sigmoid",
            )
        )

        loss = "binary_crossentropy"

    else:
        model.add(
            tf.keras.layers.Dense(
                n_classes,
                activation="softmax",
            )
        )

        loss = "sparse_categorical_crossentropy"

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-3
        ),
        loss=loss,
    )

    return model


def train_mlp(
    model,
    X_train,
    y_train,
    X_val,
    y_val,
    class_weight,
    n_classes,
    epochs=100,
    batch_size=256,
):

    macro_f1_callback = MacroF1Callback(
        X_val=X_val,
        y_val=y_val,
        n_classes=n_classes,
    )

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_macro_f1",
        mode="max",
        patience=10,
        restore_best_weights=True,
        verbose=1,
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(
            X_val,
            y_val,
        ),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=[
            macro_f1_callback,
            early_stopping,
        ],
        verbose=1,
    )

    return history

def build_optimized_mlp(
    input_dim,
    hidden_units,
    dropout_rate,
    l2_strength,
    learning_rate,
    random_state=42
):

    tf.keras.utils.set_random_seed(
        random_state
    )

    model = Sequential()

    model.add(
        Input(shape=(input_dim,))
    )

    for units in hidden_units:

        model.add(
            Dense(
                units,
                activation="relu",
                kernel_regularizer=l2(
                    l2_strength
                )
            )
        )

        if dropout_rate > 0:
            model.add(
                Dropout(dropout_rate)
            )

    model.add(
        Dense(
            1,
            activation="sigmoid"
        )
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=learning_rate
        ),
        loss="binary_crossentropy"
    )

    return model

def optimize_mlp(
    data,
    param_space,
    n_iter=15,
    max_epochs=100,
    patience=8,
    random_state=42
):

    X_train = (
        data["X_train"]
        .to_numpy(dtype=np.float32)
    )

    X_val = (
        data["X_val"]
        .to_numpy(dtype=np.float32)
    )

    y_train = (
        data["y_train"]
        .to_numpy(dtype=np.int32)
    )

    y_val = (
        data["y_val"]
        .to_numpy(dtype=np.int32)
    )

    sampled_params = list(
        ParameterSampler(
            param_space,
            n_iter=n_iter,
            random_state=random_state
        )
    )

    balanced_class_weight = get_class_weights(
        y_train
    )

    results = []

    for i, params in enumerate(
        sampled_params,
        start=1
    ):

        tf.keras.backend.clear_session()

        start_time = perf_counter()

        model = build_optimized_mlp(
            input_dim=X_train.shape[1],
            hidden_units=params[
                "hidden_units"
            ],
            dropout_rate=params[
                "dropout_rate"
            ],
            l2_strength=params[
                "l2_strength"
            ],
            learning_rate=params[
                "learning_rate"
            ],
            random_state=random_state
        )

        if (
            params["class_weight_mode"]
            == "balanced"
        ):
            class_weight = (
                balanced_class_weight
            )
        else:
            class_weight = None

        early_stopping = EarlyStopping(
            monitor="val_loss",
            patience=patience,
            restore_best_weights=True,
            mode="min"
        )

        history = model.fit(
            X_train,
            y_train,
            validation_data=(
                X_val,
                y_val
            ),
            epochs=max_epochs,
            batch_size=params[
                "batch_size"
            ],
            class_weight=class_weight,
            callbacks=[
                early_stopping
            ],
            verbose=0
        )

        train_prob = model.predict(
            X_train,
            batch_size=4096,
            verbose=0
        ).ravel()

        val_prob = model.predict(
            X_val,
            batch_size=4096,
            verbose=0
        ).ravel()

        train_pred = (
            train_prob >= 0.5
        ).astype(int)

        val_pred = (
            val_prob >= 0.5
        ).astype(int)

        train_f1_macro = f1_score(
            y_train,
            train_pred,
            average="macro",
            zero_division=0
        )

        val_f1_macro = f1_score(
            y_val,
            val_pred,
            average="macro",
            zero_division=0
        )

        val_balanced_accuracy = (
            balanced_accuracy_score(
                y_val,
                val_pred
            )
        )

        val_f1_weighted = f1_score(
            y_val,
            val_pred,
            average="weighted",
            zero_division=0
        )

        val_losses = history.history[
            "val_loss"
        ]

        best_epoch = (
            int(np.argmin(val_losses))
            + 1
        )

        elapsed_time = (
            perf_counter()
            - start_time
        )

        results.append({
            "iteration": i,
            "hidden_units": json.dumps(
                list(
                    params[
                        "hidden_units"
                    ]
                )
            ),
            "dropout_rate": params[
                "dropout_rate"
            ],
            "l2_strength": params[
                "l2_strength"
            ],
            "learning_rate": params[
                "learning_rate"
            ],
            "batch_size": params[
                "batch_size"
            ],
            "class_weight_mode": params[
                "class_weight_mode"
            ],
            "epochs_trained": len(
                history.history["loss"]
            ),
            "best_epoch": best_epoch,
            "best_val_loss": float(
                np.min(val_losses)
            ),
            "train_f1_macro": (
                train_f1_macro
            ),
            "val_f1_macro": (
                val_f1_macro
            ),
            "overfit_gap": (
                train_f1_macro
                - val_f1_macro
            ),
            "val_balanced_accuracy": (
                val_balanced_accuracy
            ),
            "val_f1_weighted": (
                val_f1_weighted
            ),
            "training_time_s": (
                elapsed_time
            )
        })

        print(
            f"{i:02d}/{len(sampled_params)} | "
            f"Val F1: {val_f1_macro:.4f} | "
            f"Train F1: {train_f1_macro:.4f} | "
            f"Gap: "
            f"{train_f1_macro - val_f1_macro:.4f} | "
            f"Epoch: {best_epoch}"
        )

    results_df = pd.DataFrame(
        results
    )

    results_df = (
        results_df
        .sort_values(
            by=[
                "val_f1_macro",
                "overfit_gap",
                "val_balanced_accuracy"
            ],
            ascending=[
                False,
                True,
                False
            ]
        )
        .reset_index(drop=True)
    )

    return results_df

def validate_mlp_temporally(
    configs,
    train_df,
    source_data,
    validation_months,
    max_epochs=100,
    patience=8,
    random_state=42
):

    results = []

    features = source_data[
        "original_features"
    ]

    for _, config in configs.iterrows():

        config_id = int(
            config["config_id"]
        )

        hidden_units = tuple(
            json.loads(
                config["hidden_units"]
            )
        )

        print(
            f"\n{'=' * 80}"
        )
        print(
            f"Configuración {config_id}"
        )
        print(
            f"{'=' * 80}"
        )

        for month in validation_months:

            print(
                f"Validación mes {month:02d}"
            )

            fold_train = (
                train_df[
                    train_df["mes_validation"]
                    != month
                ]
                .copy()
                .reset_index(drop=True)
            )

            fold_val = (
                train_df[
                    train_df["mes_validation"]
                    == month
                ]
                .copy()
                .reset_index(drop=True)
            )

            fold_train_numeric = (
                convert_model_dtypes(
                    fold_train
                )
            )

            fold_val_numeric = (
                convert_model_dtypes(
                    fold_val
                )
            )

            (
                X_train_fold,
                X_val_fold,
                used_features,
                scaler,
            ) = prepare_model_features(
                train_df=fold_train_numeric,
                test_df=fold_val_numeric,
                features=features,
                accepts_nan=False,
                scale=True,
            )

            X_train_fold = (
                X_train_fold
                .to_numpy(
                    dtype=np.float32
                )
            )

            X_val_fold = (
                X_val_fold
                .to_numpy(
                    dtype=np.float32
                )
            )

            y_train_fold = (
                fold_train[
                    "codigo_ghi"
                ]
                .to_numpy(
                    dtype=np.int32
                )
            )

            y_val_fold = (
                fold_val[
                    "codigo_ghi"
                ]
                .to_numpy(
                    dtype=np.int32
                )
            )

            classes = np.unique(
                y_train_fold
            )

            if (
                config["class_weight_mode"]
                == "balanced"
            ):

                weights = (
                    compute_class_weight(
                        class_weight="balanced",
                        classes=classes,
                        y=y_train_fold
                    )
                )

                class_weight = dict(
                    zip(
                        classes,
                        weights
                    )
                )

            else:

                class_weight = None

            tf.keras.backend.clear_session()

            model = build_optimized_mlp(
                input_dim=(
                    X_train_fold.shape[1]
                ),
                hidden_units=hidden_units,
                dropout_rate=float(
                    config["dropout_rate"]
                ),
                l2_strength=float(
                    config["l2_strength"]
                ),
                learning_rate=float(
                    config["learning_rate"]
                ),
                random_state=random_state
            )

            early_stopping = EarlyStopping(
                monitor="val_loss",
                patience=patience,
                restore_best_weights=True,
                mode="min"
            )

            start_time = perf_counter()

            history = model.fit(
                X_train_fold,
                y_train_fold,
                validation_data=(
                    X_val_fold,
                    y_val_fold
                ),
                epochs=max_epochs,
                batch_size=int(
                    config["batch_size"]
                ),
                class_weight=class_weight,
                callbacks=[
                    early_stopping
                ],
                verbose=0
            )

            train_prob = (
                model.predict(
                    X_train_fold,
                    batch_size=4096,
                    verbose=0
                )
                .ravel()
            )

            val_prob = (
                model.predict(
                    X_val_fold,
                    batch_size=4096,
                    verbose=0
                )
                .ravel()
            )

            train_pred = (
                train_prob >= 0.5
            ).astype(int)

            val_pred = (
                val_prob >= 0.5
            ).astype(int)

            train_f1 = f1_score(
                y_train_fold,
                train_pred,
                average="macro",
                zero_division=0
            )

            val_f1 = f1_score(
                y_val_fold,
                val_pred,
                average="macro",
                zero_division=0
            )

            val_balanced_acc = (
                balanced_accuracy_score(
                    y_val_fold,
                    val_pred
                )
            )

            val_f1_weighted = (
                f1_score(
                    y_val_fold,
                    val_pred,
                    average="weighted",
                    zero_division=0
                )
            )

            val_losses = (
                history.history[
                    "val_loss"
                ]
            )

            best_epoch = (
                int(
                    np.argmin(
                        val_losses
                    )
                )
                + 1
            )

            elapsed_time = (
                perf_counter()
                - start_time
            )

            results.append({
                "config_id": (
                    config_id
                ),
                "validation_month": (
                    month
                ),
                "hidden_units": (
                    config[
                        "hidden_units"
                    ]
                ),
                "dropout_rate": float(
                    config[
                        "dropout_rate"
                    ]
                ),
                "l2_strength": float(
                    config[
                        "l2_strength"
                    ]
                ),
                "learning_rate": float(
                    config[
                        "learning_rate"
                    ]
                ),
                "batch_size": int(
                    config[
                        "batch_size"
                    ]
                ),
                "class_weight_mode": (
                    config[
                        "class_weight_mode"
                    ]
                ),
                "best_epoch": (
                    best_epoch
                ),
                "epochs_trained": len(
                    history.history[
                        "loss"
                    ]
                ),
                "train_f1_macro": (
                    train_f1
                ),
                "val_f1_macro": (
                    val_f1
                ),
                "overfit_gap": (
                    train_f1
                    - val_f1
                ),
                "abs_gap": abs(
                    train_f1
                    - val_f1
                ),
                "val_balanced_accuracy": (
                    val_balanced_acc
                ),
                "val_f1_weighted": (
                    val_f1_weighted
                ),
                "training_time_s": (
                    elapsed_time
                )
            })

            print(
                f"  F1 val: "
                f"{val_f1:.4f} | "
                f"F1 train: "
                f"{train_f1:.4f} | "
                f"best epoch: "
                f"{best_epoch}"
            )

    return pd.DataFrame(
        results
    )